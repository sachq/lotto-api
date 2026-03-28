import io
import logging
import ssl
import urllib.request
import urllib.error
import certifi
from datetime import date

import pandas as pd
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from app.api.db.models import LottoDraw, LottoType
from app.config import get_settings

logger = logging.getLogger(__name__)


class LottoDataError(Exception):
    """Custom exception for LottoData errors."""
    pass


class LottoData:
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds

    def __init__(self):
        self._data_urls = {
            'Powerball': 'https://data.ny.gov/api/views/d6yy-54nr/rows.csv'
                         '?accessType=DOWNLOAD',
            'Megamillion': 'https://data.ny.gov/api/views/5xaw-6ayf/rows.csv'
                           '?accessType=DOWNLOAD'
        }

        settings = get_settings()
        self.Session = sessionmaker(
            bind=create_engine(settings.POSTGRES_DB_URI))

        self._winning_cols = ['A', 'B', 'C', 'D', 'E']
        self._jackpot_col = 'J'
        winning_cols_copy = self._winning_cols.copy()
        winning_cols_copy.extend([self._jackpot_col])
        self._winning_cols_with_jackpot = winning_cols_copy

        # Cache for lotto type IDs
        self._lotto_type_ids = None

    def _get_lotto_type_id(self, lotto_name: str) -> int:
        """
        Gets the lotto type ID from the database by name.
        Caches the results to avoid repeated queries.
        """
        if self._lotto_type_ids is None:
            session = self.Session()
            try:
                lotto_types = session.query(LottoType).filter(
                    LottoType.is_active == True).all()
                self._lotto_type_ids = {lt.name: lt.id for lt in lotto_types}
            finally:
                session.close()

        if lotto_name not in self._lotto_type_ids:
            raise LottoDataError(f"Unknown lotto type: {lotto_name}")

        return self._lotto_type_ids[lotto_name]

    def process_remote_lotto(self):
        """
        Cleans CSV data for each Lotto Dataset, Adds new lotto data to the
        DB if it finds new Lotto Draw Data from the remote file.
        """
        session = self.Session()
        try:
            for lotto_name in self._data_urls:
                logger.info(f"Analysing '{lotto_name}'")
                print(f'\nAnalysing \'{lotto_name}\'')

                try:
                    # gets the last updated draw date on the DB
                    date_filter = pd.to_datetime(
                        self._get_last_updated_draw_date(lotto_name))

                    # Fetch Cleaned Lotto Draw Data
                    df = self._fetch_draw_data(lotto_name)
                    latest_draws = df[df['draw_date'] > date_filter]
                    draws_arr = latest_draws.to_dict(orient='records')

                    # Update DB lotto draw table with the latest Draw Data
                    if len(draws_arr):
                        print('Updating Lotto Draw Data: ')
                        added = 0
                        for draw in draws_arr:
                            exists = session.query(LottoDraw).filter(
                                LottoDraw.draw_date == draw['draw_date'],
                                LottoDraw.lotto_type_id == draw['lotto_type_id']
                            ).first()
                            if exists:
                                logger.info(f"Skipping duplicate draw: {draw['draw_date']}")
                                continue
                            new_draw = LottoDraw(**draw)
                            session.add(new_draw)
                            print(f'* -> Added new draw from {draw["draw_date"]}')
                            added += 1
                        session.commit()
                        logger.info(f"Added {added} new draws for {lotto_name}")
                    else:
                        print(f'* Nothing new to add for \'{lotto_name}\'\n')
                        logger.info(f"No new draws for {lotto_name}")

                except LottoDataError as e:
                    logger.error(f"Error processing {lotto_name}: {e}")
                    print(f"Error processing {lotto_name}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error processing {lotto_name}: {e}")
                    print(f"Unexpected error processing {lotto_name}: {e}")
                    session.rollback()
                    continue
        finally:
            session.close()

    def _get_last_updated_draw_date(self, lotto_name):
        """
        Gets the Last updated Draw from the DB for the Given Lotto.
        :param lotto_name: Name of the lotto type
        :return: Last draw date as pandas datetime
        """
        session = self.Session()
        try:
            last_draw = session.query(LottoDraw).join(LottoType).filter(
                LottoType.name == lotto_name,
                LottoDraw.is_active == True
            ).order_by(desc(LottoDraw.draw_date)).first()

            last_drawn_date = date(2000, 1, 1)
            if last_draw is not None:
                last_drawn_date = last_draw.draw_date

            print(f'Last Draw Date: {last_drawn_date}')
            logger.info(f"Last draw date for {lotto_name}: {last_drawn_date}")
            return pd.to_datetime(last_drawn_date)
        finally:
            session.close()

    def _fetch_draw_data(self, lotto_name):
        """
        Fetches the latest updated Lotto Draw data from a remote data
        repository with proper SSL verification and retry logic.
        :param lotto_name: Name of the lotto to fetch
        :return: Cleaned data from the respective lotto
        :raises LottoDataError: If fetching fails after all retries
        """
        import time

        # Use proper SSL verification with certifi certificates
        context = ssl.create_default_context(cafile=certifi.where())

        data_url = self._data_urls[lotto_name]
        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                response = urllib.request.urlopen(
                    data_url, context=context, timeout=30)
                data = response.read().decode('utf-8')

                df = pd.read_csv(io.StringIO(data))
                if df.empty:
                    raise LottoDataError(f"Empty data received for {lotto_name}")

                df['Draw Date'] = pd.to_datetime(df['Draw Date'])
                df = df.sort_values('Draw Date', ascending=True)

                return self._clean_lotto_data(df, lotto_name)

            except urllib.error.URLError as e:
                last_error = e
                logger.warning(
                    f"Attempt {attempt + 1}/{self.MAX_RETRIES} failed for "
                    f"{lotto_name}: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY * (attempt + 1))
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Attempt {attempt + 1}/{self.MAX_RETRIES} failed for "
                    f"{lotto_name}: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY * (attempt + 1))

        raise LottoDataError(
            f"Failed to fetch data for {lotto_name} after {self.MAX_RETRIES} "
            f"attempts: {last_error}")

    def _clean_lotto_data(self, dataframe, lotto_name):
        """
        Cleans lotto draw data from CSV format.
        :param dataframe: Raw dataframe from CSV
        :param lotto_name: Name of the lotto type
        :return: Cleaned dataframe ready for database insertion
        """
        df = dataframe.copy()
        reindex_cols = self._winning_cols_with_jackpot.copy()
        reindex_cols.extend(['draw_date', 'lotto_type_id'])
        df['draw_date'] = df['Draw Date']
        cols_to_drop = ['Draw Date', 'Winning Numbers', 'Multiplier']

        # Get lotto type ID from database instead of hardcoding
        lotto_type_id = self._get_lotto_type_id(lotto_name)
        df['lotto_type_id'] = lotto_type_id

        if lotto_name == 'Megamillion':
            df[self._winning_cols] = df['Winning Numbers'].str.split(' ',
                                                                     expand=True)
            df[self._jackpot_col] = df['Mega Ball']
            cols_to_drop.extend(['Mega Ball'])
        else:
            df[self._winning_cols_with_jackpot] = df[
                'Winning Numbers'].str.split(' ', expand=True)

        df.drop(cols_to_drop, axis=1, inplace=True, errors='ignore')
        df = df.reindex(columns=reindex_cols)

        # Convert number columns to integers
        for col in self._winning_cols_with_jackpot:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

        return df


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    lotto_data = LottoData()
    lotto_data.process_remote_lotto()
