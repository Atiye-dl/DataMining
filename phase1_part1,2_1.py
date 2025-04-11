import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns

data = pd.read_csv('GooglePlay.csv')

data['Installs'] = data['Installs'].str.replace('+', '')
data['Installs'] = data['Installs'].str.replace(',', '')
data['Installs'] = pd.to_numeric(data['Installs'], errors='coerce').astype('Int64')

data['Size'] = data['Size'].str.replace('M', '')
data['Size'] = pd.to_numeric(data['Size'], errors='coerce')

data['Price'] = data['Price'].str.replace('$', '')
data['Price'] = pd.to_numeric(data['Price'], errors='coerce')

data['Reviews'] = pd.to_numeric(data['Reviews'], errors='coerce').astype('Int64')

data['Rating'] = pd.to_numeric(data['Rating'], errors='coerce')

numeric_columns = ['Installs', 'Price', 'Size', 'Reviews', 'Rating']

df = pd.DataFrame()

df['Feature name'] = numeric_columns

types = []
means = []
medians = []
mins = []
maxs = []
modes = []
reanges = []
num_outliers = []
for column in numeric_columns:
    print('--------- ' + column + ' ----------')
    types.append(data[column].dtypes)
    print('Type: ' + str(data[column].dtypes))

    means.append(round(data[column].dropna().mean(), 2))
    print('Mean: ' + str(round(data[column].dropna().mean(), 2)))

    medians.append(data[column].dropna().median())
    print('Median: ' + str(data[column].dropna().median()))


    data_min = data[column].dropna().min()
    data_max = data[column].dropna().max()

    mins.append(data_min)
    print('Min: ' + str(data_min))

    maxs.append(data_max)
    print('Max: ' + str(data_max))

    modes.append(data[column].dropna().mode().iloc[0])
    print('Mode: ' + str(data[column].dropna().mode().iloc[0]))

    reanges.append(str(data_min) + ' to ' + str(data_max))
    print('Range: ' + str(data_min) + ' to ' + str(data_max))
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    outliers = data[column][(data[column] < (Q1 - 1.5 * IQR)) | (data[column] > (Q3 + 1.5 * IQR))]
    print('Outliers: ' + str(outliers))
    num_outliers.append(outliers.size)
    print()

df['Types'] = types
df['Means'] = means
df['Medians'] = medians
df['mins'] = mins
df['maxs'] = maxs
df['modes'] = modes
df['ranges'] = reanges
df['number of outliers'] = num_outliers
print(df.head())
fig, axs = plt.subplots(2, 3)
i = 0
j = 0
for column in numeric_columns:

    axs[i, j].boxplot(data[column].dropna())
    axs[i, j].set_title(column)
    i += 1
    if i == 2:
        i = 0
        j += 1

for ax in axs.flat:
    ax.set(xlabel='x-label', ylabel='y-label')

plt.show()