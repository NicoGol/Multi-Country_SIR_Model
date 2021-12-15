import pandas as pd

df_fb = pd.read_csv('../data/movement_countries.csv')
countries = sorted(df_fb.end_name.unique())
df_fb.rename(columns = {'ds':'date'}, inplace = True)


countries_name = ['austria','belgium' ,'croatia' ,'czechia' ,'denmark',
 'estonia' ,'finland' ,'france' ,'germany', 'greece', 'iceland', 'ireland',
 'italy','lithuania' ,'luxembourg', 'netherlands', 'norway',
 'romania', 'serbia', 'spain', 'sweden', 'switzerland',
 'united kingdom', 'portugal', 'slovenia',  'hungary', 'poland',
 'bosnia and herzegovina', 'slovakia', 'bulgaria' ]

df_fb = df_fb.replace({"start_name": {"czech republic":"czechia"}})
df_fb = df_fb.replace({"end_name": {"czech republic":"czechia"}})



df_fb = df_fb[df_fb['end_name'].isin(['austria','belgium' ,'croatia' ,'czechia' ,'denmark',
 'estonia' ,'finland' ,'france' ,'germany', 'greece', 'iceland', 'ireland',
 'italy','lithuania' ,'luxembourg', 'netherlands', 'norway',
 'romania', 'serbia', 'spain', 'sweden', 'switzerland',
 'united kingdom', 'portugal', 'slovenia',  'hungary', 'poland',
 'bosnia and herzegovina', 'slovakia', 'bulgaria'])]

df_fb = df_fb[df_fb['start_name'].isin(['austria','belgium' ,'croatia' ,'czechia' ,'denmark',
 'estonia' ,'finland' ,'france' ,'germany', 'greece', 'iceland', 'ireland',
 'italy','lithuania' ,'luxembourg', 'netherlands', 'norway',
 'romania', 'serbia', 'spain', 'sweden', 'switzerland',
 'united kingdom', 'portugal', 'slovenia',  'hungary', 'poland',
 'bosnia and herzegovina', 'slovakia', 'bulgaria' ])]


baseline_start = '2020-02-29'
baseline_end = '2020-03-06'

migration_matrix = df_fb[df_fb.date <= baseline_end]
migration_matrix = migration_matrix[migration_matrix.date >= baseline_start]
migration_matrix = migration_matrix.groupby(['start_name', 'end_name']).agg({'travel_counts': 'mean'}).reset_index()

df_scaling = pd.read_csv('../data/scaling.csv')
migration_matrix = pd.merge(migration_matrix, df_scaling, how='left', left_on=['start_name','end_name'],
                            right_on=['Origin','Destination'])

migration_matrix['rescaling'] = migration_matrix['rescaling'].fillna(4)
migration_matrix['travel_counts'] = migration_matrix['travel_counts']*migration_matrix['rescaling']

migration_matrix['traffic'] = 0
for index, row in migration_matrix.iterrows():
    val1 = row['travel_counts']
    val2 = migration_matrix.loc[(migration_matrix.start_name==row['end_name'])&(migration_matrix.end_name==row['start_name'])]['travel_counts'].values
    if len(val2) > 0:
        val2 = val2[0]
    else:
        val2 = 0.0
    migration_matrix['traffic'].loc[index] = (val1+val2)/2
migration_matrix = migration_matrix.pivot_table(columns='end_name', index='start_name', values='traffic').fillna(0.0)
migration_matrix.to_csv('../data/migration_matrix.csv')
