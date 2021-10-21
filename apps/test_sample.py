import pandas as pd
from home import update_cases, update_deaths

data1 = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'
df1 = pd.read_csv(data1)
total_cases1 = df1.loc[df1.location == 'World', ['total_cases']].max()
total_deaths2 = df1.loc[df1.location == 'World', ['total_deaths']].max()


def test_update_cases():
    result = update_cases.__wrapped__(1)
    assert (result == total_cases1).all()

def test_update_deaths():
    result = update_deaths.__wrapped__(1)
    assert (result == total_deaths2).all()