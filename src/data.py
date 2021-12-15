import numpy as np
import pandas as pd


europe_countries = ['austria', 'belgium', 'bosnia and herzegovina', 'bulgaria', 'croatia',
       'czechia', 'denmark', 'estonia', 'finland', 'france', 'germany',
       'greece', 'hungary', 'iceland', 'ireland', 'italy', 'lithuania',
       'luxembourg', 'netherlands', 'norway', 'poland', 'portugal', 'romania',
       'serbia', 'slovakia', 'slovenia', 'spain', 'sweden', 'switzerland',
       'united kingdom']

#csv file containing daily data about the covid-19 (new deaths and cases) in every country
df_owid = pd.read_csv('../data/owid.csv')
df_owid['location'] = df_owid['location'].str.lower()



df_owid.replace({"location": {"czech republic":"czechia"}})



countries = sorted(df_owid.location.unique())

df_owid = df_owid[['date','location','iso_code','new_cases_smoothed_per_million',
                   'continent','population',
                   'new_cases_smoothed','reproduction_rate','stringency_index']]

df_owid = df_owid[df_owid['location'].isin(europe_countries)]


pop = df_owid.groupby(['location','iso_code']).agg({'population':'max'}).reset_index()#.set_index('location')

#csv file containing information about the location (longitude, latitude) of countries
df_countries = pd.read_csv('../data/countries.csv')

# filter eu countries
df_countries['Country'] = df_countries['Country'].str.lower()
df_countries = df_countries[df_countries['Country'].isin(europe_countries)]
latitude = df_countries.set_index(['Country']).to_dict(orient='dict')['Latitude']
longitude = df_countries.set_index(['Country']).to_dict(orient='dict')['Longitude']

df_countries = pd.merge(pop, df_countries, how='left', left_on='location', right_on='Country').drop(columns=['location']).set_index('Country')
df_countries['Country'] = df_countries.index


# ---------------- data --------------

horizon = 350

eu_countries = ['austria', 'belgium', 'bosnia and herzegovina', 'bulgaria', 'croatia' ,'czechia' ,'denmark',
 'estonia' ,'finland' ,'france' ,'germany', 'greece', 'hungary', 'iceland', 'ireland',
 'italy','lithuania' ,'luxembourg', 'netherlands', 'norway', 'poland', 'portugal',
 'romania', 'serbia', 'slovakia', 'slovenia', 'spain', 'sweden', 'switzerland', 'united kingdom']


order_countries = ['iceland','finland','sweden','norway','united kingdom','ireland','denmark','estonia','lithuania',
                   'netherlands','germany','belgium','france','luxembourg','poland','czechia','slovakia','hungary',
                   'switzerland','austria','italy','spain','portugal','slovenia','croatia',
                   'serbia','bosnia and herzegovina','romania','bulgaria','greece']

migration_matrix_df = pd.read_csv('../data/migration_matrix.csv', index_col='start_name')

migration_matrix_baseline = migration_matrix_df.copy()

def to_code(country):
    return df_countries['ISO 3166 Country Code'][country]
migration_matrix_short = migration_matrix_df.copy().rename(columns=to_code)
migration_matrix_short = migration_matrix_short / 1000
migration_matrix_short = migration_matrix_short.apply(round)
migration_matrix_short = migration_matrix_short.reset_index().rename(columns={'start_name':''})
migration_matrix_short[''] = migration_matrix_short[''].apply(to_code)

def create_migration_matrix(Horizon=350):
    """
    Function creating the 3 dimensional migration matrix containing the number of daily movers between each pair of
    european country for each time step
    :param Horizon: the range of time period in terms of days for the simulation
    :return:  the migration matrix containing the number of daily movers between each pair of country for each time step.
    The shape of the matrix is (Horizon,len(europe_countries),len(europe_countries)).
    """
    return np.array([migration_matrix_short.values[:,1:] for i in range(Horizon)])
