import io
import ssl
import urllib.request
from datetime import date

import pandas as pd
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from app.api.db.models import LottoDraw, LottoType
from app.config import get_settings


class LottoData:
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

    def process_remote_lotto(self):
        """
        Cleans CSV data for each Lotto Dataset, Adds new lotto data to the
        DB if it finds new Lotto Draw Data from the remote file.
        """
        session = self.Session()
        for lotto_name in self._data_urls:
            print(f'\nAnalysing \'{lotto_name}\'')

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
                for draw in draws_arr:
                    new_draw = LottoDraw(**draw)
                    session.add(new_draw)
                    print(f'* -> Added new draw from {draw["draw_date"]}')
                session.commit()
                session.close()
            else:
                print(f'* Nothing new to add for \'{lotto_name}\'')

    def _get_last_updated_draw_date(self, lotto_name):
        """
        Gets the Last updated Draw from the DB for the Given Lotto
        :param lotto_name:
        :return:
        """
        session = self.Session()
        last_draw = session.query(LottoDraw).join(LottoType).filter(
            LottoType.name == lotto_name).order_by(
            desc(LottoDraw.draw_date)).first()
        session.close()

        last_drawn_date = date(2000, 1, 1)
        if last_draw is not None:
            last_drawn_date = last_draw.draw_date

        print(f'Last Draw Date: {last_drawn_date}')
        return pd.to_datetime(last_drawn_date)

    def _fetch_draw_data(self, lotto_name):
        """
        Fetches the latest updated Lotto Draw data from a remote data
        repository.
        :param lotto_name Name of the lotto to fetch
        :return Cleaned data from the respective lotto
        """
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        data_url = self._data_urls[lotto_name]
        response = urllib.request.urlopen(data_url, context=context)
        data = response.read().decode('utf-8')

        df = pd.read_csv(io.StringIO(data))
        df['Draw Date'] = pd.to_datetime(df['Draw Date'])
        df = df.sort_values('Draw Date', ascending=True)

        return self._clean_lotto_data(df, lotto_name)

    def _clean_lotto_data(self, dataframe, lotto_name):
        """
        Cleans Mega
        :param dataframe:
        :return:
        """
        df = dataframe.copy()
        reindex_cols = self._winning_cols_with_jackpot.copy()
        reindex_cols.extend(['draw_date', 'lotto_type_id'])
        df['draw_date'] = pd.to_datetime(df['Draw Date'], format='%m/%d/%y')
        cols_to_drop = ['Draw Date', 'Winning Numbers', 'Multiplier']
        if lotto_name == 'Megamillion':
            df['lotto_type_id'] = 1
            df[self._winning_cols] = df['Winning Numbers'].str.split(' ',
                                                                     expand=True)
            df[self._jackpot_col] = df['Mega Ball']
            cols_to_drop.extend(['Mega Ball'])
        else:
            df['lotto_type_id'] = 2
            df[self._winning_cols_with_jackpot] = df[
                'Winning Numbers'].str.split(' ', expand=True)
        df.drop(cols_to_drop, axis=1, inplace=True)
        df = df.reindex(columns=reindex_cols)

        return df


if __name__ == "__main__":
    lotto_data = LottoData()
    lotto_data.process_remote_lotto()
