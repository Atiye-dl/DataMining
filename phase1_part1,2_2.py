import pandas as pd

data = pd.read_csv('GooglePlay.csv')

# Completeness

total_rows = len(data)

features = data.columns

numeric_columns = ['Installs', 'Price', 'Size', 'Reviews', 'Rating']

for col in numeric_columns:
    missing_values = data[col].isnull().sum()

    completeness = ((total_rows - missing_values) / total_rows) * 100

    print('Completeness of the ' + col + ' column: ' + str(round(completeness, 2)))


# Consistency

prices = data['Price']
types = data['Type']

print(data[((data['Type'] == 'Free') & (data['Price'] != '0')) | ((data['Type'] == 'Paid') & (data['Price'] == '0'))])



# Validity



# Accuracy



# Currentness


for col in data.columns:
    print('-------------------\n')
    print('column: ' + col)
    print('number of rows: ' + str(total_rows))
    null_values = data[col].isnull().sum()
    print('number of null rows: ' + str(null_values))
    print('-------------------\n')
