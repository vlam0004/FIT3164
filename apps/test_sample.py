import pandas as pd
from home import update_cases

data1 = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'
df1 = pd.read_csv(data1)
total_cases1 = df1.loc[df1.location == 'World', ['total_cases']].max()


def test_update_cases():
    assert update_cases(1) == total_cases1
