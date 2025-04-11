import pandas as pd
import re
import numpy as np
import warnings

warnings.filterwarnings('ignore')
pd.set_option('display.max_rows', 29)

date_pattern = r'(0?[1-9]|1\d|2[0-9]|3[01])-(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-(\d{2})'
version_pattern = r'\d+(\.\d+)+'
size_pattern = r'^\d+(\.\d+)?(M|K)$'
installs_pattern = r'^(\d{1,3}(,\d{3})*)\+$'
price_pattern = r'^\$?\d+(\.\d+)?$'
android_version_pattern = r'^\d+(\.\d+)*$'
app_id_pattern = r'^[a-zA-Z0-9_\.]+$'
email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
developer_website_pattern = r'^(https?:\/\/)[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+([\/?#]\S*)?$'
privacy_policy_pattern = r'^(https?:\/\/)[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+([\/?#]\S*)?$'
summary_pattern = r'^[a-zA-Z0-9.,\/?&|!+\-*()]+$'
developer_pattern = r'^[a-zA-Z0-9.+&-,()]+$'
developer_address_pattern = r'^[a-zA-Z0-9.,\/&|!+\-()]+$'
developer_id_pattern = r'^[a-zA-Z0-9.,+]+$'

data = pd.read_csv('Playstore_final.csv')
features = data.columns.tolist()[:29]

def calculate_outliers(column):
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    return data[column][(data[column] < (Q1 - 1.5 * IQR)) | (data[column] > (Q3 + 1.5 * IQR))]

def get_clean_column(column, pattern = None):
    if pattern != None:
        return data[column][data[column].apply(lambda row: re.match(pattern, str(row)) != None)].dropna()
    else:
        return data[column][data[column].apply(lambda row: str(row) != 'N/A')].dropna()

def date_split(date):
    try:
        return int(date.split('-')[2]) >= 16
    except:
        return False

total_rows = len(data)

df = pd.DataFrame()
df['Features'] = features
completeness_list = []
currentness_list = [100 for i in range(len(features))]
validity_list = []
accuracy_list = []
consistency_list = [100 for i in range(len(features))]
number_nulls = []
number_rows = []

# Completeness

for col in features:
    missing_values = data[col].isnull().sum()
    completeness = ((total_rows - missing_values) / total_rows) * 100
    completeness_list.append(str(round(completeness, 2)))
    number_nulls.append(missing_values)


# Currentness

# Last Update
last_update_clean = get_clean_column('Last update', date_pattern)
last_update_currentness = last_update_clean[last_update_clean.apply(lambda row: date_split(str(row)))]
last_update_currentness = len(last_update_currentness)
last_update_currentness = str(round(((last_update_currentness) / total_rows) * 100, 2))
currentness_list[features.index('Last update')] = last_update_currentness

# Released
released_clean = get_clean_column('Released', date_pattern)
released_currentness = released_clean[released_clean.apply(lambda row: date_split(str(row)))]
released_currentness = len(released_currentness)
released_currentness = str(round(((released_currentness) / total_rows) * 100, 2))
currentness_list[features.index('Released')] = released_currentness


# Consistency
price_and_free_consistency = len(data[((data['Free'] == 'TRUE') & (data['Price'] != '0')) | ((data['Free'] == 'FALSE') & (data['Price'] == '0'))])
price_and_free_consistency = str(round(((total_rows - price_and_free_consistency) / total_rows) * 100, 2))
consistency_list[features.index('Price')] = price_and_free_consistency
consistency_list[features.index('Free')] = price_and_free_consistency

android_version_clean = data['Android version Text'].str.replace(' and up', '')
android_version_and_minimum = len(data[((data['Android version Text'] == 'Varies with device') & (data['Minimum Android'] == 'Varies')) | (data['Minimum Android'] <= data['Android version Text'])])
android_version_and_minimum = str(round(((android_version_and_minimum) / total_rows) * 100, 2))
consistency_list[features.index('Android version Text')] = android_version_and_minimum
consistency_list[features.index('Minimum Android')] = android_version_and_minimum

installs_clean = data['Installs'].str.replace('+', '')
installs_clean = installs_clean.str.replace(',', '')
installs_clean = pd.to_numeric(installs_clean, errors='coerce').astype('Int64')
reviews_clean = pd.to_numeric(data['Reviews'], errors='coerce').astype('Int64')
installs_and_reviews_consistency = len(data[reviews_clean > installs_clean])
installs_and_reviews_consistency = str(round(((total_rows - installs_and_reviews_consistency) / total_rows) * 100, 2))
consistency_list[features.index('Reviews')] = installs_and_reviews_consistency
consistency_list[features.index('Installs')] = installs_and_reviews_consistency


# Validity and Accuracy
validity_list.append(100)
accuracy_list.append(100)

# App Id
app_id_clean = get_clean_column('App Id')
app_id_valid = len(app_id_clean[app_id_clean.apply(lambda row: re.match(app_id_pattern, row) != None)])
app_id_accuracy = str(round(((app_id_valid) / total_rows) * 100, 2))
app_id_valid = str(round(((app_id_valid) / len(app_id_clean)) * 100, 2))
validity_list.append(app_id_valid)
accuracy_list.append(app_id_accuracy)

# Category
category_clean = get_clean_column('Category')
categories = category_clean.unique()
valid_categories = len(category_clean[category_clean.apply(lambda row: row in categories)])
accuracy_categories = str(round(((valid_categories) / total_rows) * 100, 2))
valid_categories = str(round(((valid_categories) / len(category_clean)) * 100, 2))
validity_list.append(valid_categories)
accuracy_list.append(accuracy_categories)

# Rating
rating_clean = get_clean_column('Rating')
rating_outliers = len(calculate_outliers('Rating'))
accuracy_rating = str(round(((len(rating_clean) - rating_outliers) / total_rows) * 100, 2))
rating_outliers = str(round(((len(rating_clean) - rating_outliers) / len(rating_clean)) * 100, 2))
validity_list.append(rating_outliers)
accuracy_list.append(accuracy_rating)

# Rating Count
rating_count_clean = get_clean_column('Rating Count')
rating_count_outliers = len(calculate_outliers('Rating Count'))
accuracy_rating_count = str(round(((len(rating_count_clean) - rating_count_outliers) / total_rows) * 100, 2))
rating_count_outliers = str(round(((len(rating_count_clean) - rating_count_outliers) / len(rating_count_clean)) * 100, 2))
validity_list.append(rating_count_outliers)
accuracy_list.append(accuracy_rating_count)

# Installs
installs_clean = get_clean_column('Installs')
installs_valid = len(installs_clean[installs_clean.apply(lambda row: re.match(installs_pattern, str(row)) != None)])
accuracy_installs = str(round(((installs_valid) / total_rows) * 100, 2))
installs_valid = str(round(((installs_valid) / len(installs_clean)) * 100, 2))
validity_list.append(installs_valid)
accuracy_list.append(accuracy_installs)

# Minimum Installs
minimum_installs_clean = get_clean_column('Minimum Installs')
minimum_installs_outliers = len(calculate_outliers('Minimum Installs'))
accuracy_minimum_installs = str(round(((len(minimum_installs_clean) - minimum_installs_outliers) / total_rows) * 100, 2))
minimum_installs_outliers = str(round(((len(minimum_installs_clean) - minimum_installs_outliers) / len(minimum_installs_clean)) * 100, 2))
validity_list.append(minimum_installs_outliers)
accuracy_list.append(accuracy_minimum_installs)

# Free
free_clean = get_clean_column('Free')
frees = free_clean.unique()
valid_frees = len(free_clean[free_clean.apply(lambda row: row in frees)])
accuracy_frees = str(round(((valid_frees) / total_rows) * 100, 2))
valid_frees = str(round(((valid_frees) / len(free_clean)) * 100, 2))
validity_list.append(valid_frees)
accuracy_list.append(accuracy_frees)

# Price 
price_clean = get_clean_column('Price')
price_outliers = len(calculate_outliers('Price'))
accuracy_price = str(round(((len(price_clean) - price_outliers) / total_rows) * 100, 2))
price_outliers = str(round(((len(price_clean) - price_outliers) / len(price_clean)) * 100, 2))
validity_list.append(price_outliers)
accuracy_list.append(accuracy_price)

# Currency
currency_clean = get_clean_column('Currency')
currencies = currency_clean.unique().tolist()
currencies.remove('XXX')
valid_currencies = len(currency_clean[currency_clean.apply(lambda row: row in currencies)])
accuracy_currencies = str(round(((valid_currencies) / total_rows) * 100, 2))
valid_currencies = str(round(((valid_currencies) / len(currency_clean)) * 100, 2))
validity_list.append(valid_currencies)
accuracy_list.append(accuracy_currencies)

# Size
size_clean = get_clean_column('Size')
size_valid = len(size_clean[size_clean.apply(lambda row: (re.match(size_pattern, row) != None) | (str(row) == 'Varies with device'))])
accuracy_size = str(round(((size_valid) / total_rows) * 100, 2))
size_valid = str(round(((size_valid) / len(size_clean)) * 100, 2))
validity_list.append(size_valid)
accuracy_list.append(accuracy_size)

# Minimum Android
minimum_android_clean = get_clean_column('Minimum Android')
valid_minimum_android = len(minimum_android_clean[minimum_android_clean.apply(lambda row: (re.match(android_version_pattern, str(row)) != None) | ((str(row) == 'Varies')))])
accuracy_minimum_android = str(round(((valid_minimum_android) / total_rows) * 100, 2))
valid_minimum_android = str(round(((valid_minimum_android) / len(minimum_android_clean)) * 100, 2))
validity_list.append(valid_minimum_android)
accuracy_list.append(accuracy_minimum_android)

# Developer Id
developer_id_clean = get_clean_column('Minimum Android')
valid_developer_id = len(developer_id_clean[developer_id_clean.apply(lambda row: re.match(developer_id_pattern, str(row)) != None)])
accuracy_developer_id = str(round(((valid_developer_id) / total_rows) * 100, 2))
valid_developer_id = str(round(((valid_developer_id) / len(developer_id_clean)) * 100, 2))
validity_list.append(valid_developer_id)
accuracy_list.append(accuracy_developer_id)

# Developer Website
developer_website_clean = get_clean_column('Developer Website')
developer_website_valid = len(developer_website_clean[developer_website_clean.apply(lambda row: re.match(developer_website_pattern, row) != None)])
accuracy_developer_website = str(round(((developer_website_valid) / total_rows) * 100, 2))
developer_website_valid = str(round(((developer_website_valid) / len(developer_website_clean)) * 100, 2))
validity_list.append(developer_website_valid)
accuracy_list.append(accuracy_developer_website)

# Developer Email
developer_email_clean = get_clean_column('Developer Email')
developer_email_valid = len(developer_email_clean[developer_email_clean.apply(lambda row: re.match(email_pattern, row) != None)])
accuracy_developer_email = str(round(((developer_email_valid) / total_rows) * 100, 2))
developer_email_valid = str(round(((developer_email_valid) / len(developer_email_clean)) * 100, 2))
validity_list.append(developer_email_valid)
accuracy_list.append(accuracy_developer_email)

# Released
release_clean = get_clean_column('Released')
list_of_match_dates = release_clean.apply(lambda row: re.match(date_pattern, row) == None)
n = 0
for item in list_of_match_dates:
    if item == True:
        n += 1
accuracy_release = str(round(((len(release_clean) - n) / total_rows) * 100, 2))
validity_release = str(round(((len(release_clean) - n) / len(release_clean)) * 100, 2))
validity_list.append(validity_release)
accuracy_list.append(accuracy_release)

# Last Update
last_update_clean = get_clean_column('Last update')
list_of_match_dates = last_update_clean.apply(lambda row: re.match(date_pattern, row) == None)
n = 0
for item in list_of_match_dates:
    if item == True:
        n += 1
accuracy_last_update = str(round(((len(last_update_clean) - n) / total_rows) * 100, 2))
validity_last_update = str(round(((len(last_update_clean) - n) / len(last_update_clean)) * 100, 2))
validity_list.append(validity_last_update)
accuracy_list.append(accuracy_last_update)

# Privacy Policy
privacy_policy_clean = get_clean_column('Privacy Policy')
privacy_policy_valid = len(privacy_policy_clean[privacy_policy_clean.apply(lambda row: re.match(privacy_policy_pattern, row) != None)])
accuracy_privacy_policy = str(round(((privacy_policy_valid) / total_rows) * 100, 2))
privacy_policy_valid = str(round(((privacy_policy_valid) / len(privacy_policy_clean)) * 100, 2))
validity_list.append(privacy_policy_valid)
accuracy_list.append(accuracy_privacy_policy)

# Content Rating
content_rating_clean = get_clean_column('Content Rating')
content_rating = content_rating_clean.unique()
valid_content_rating = len(content_rating_clean[content_rating_clean.apply(lambda row: row in content_rating)])
accuracy_content_rating = str(round(((valid_content_rating) / total_rows) * 100, 2))
valid_content_rating = str(round(((valid_content_rating) / len(content_rating_clean)) * 100, 2))
validity_list.append(valid_content_rating)
accuracy_list.append(accuracy_content_rating)

# Ad Supported
ad_supported_clean = get_clean_column('Ad Supported')
ad_supported = ad_supported_clean.unique()
valid_ad_supported = len(ad_supported_clean[ad_supported_clean.apply(lambda row: row in ad_supported)])
accuracy_ad_supported = str(round(((valid_ad_supported) / total_rows) * 100, 2))
valid_ad_supported = str(round(((valid_ad_supported) / len(ad_supported_clean)) * 100, 2))
validity_list.append(valid_ad_supported)
accuracy_list.append(accuracy_ad_supported)

# In app purchases
in_app_purchase_clean = get_clean_column('In app purchases')
in_app_purchase = in_app_purchase_clean.unique()
valid_in_app_purchase = len(in_app_purchase_clean[in_app_purchase_clean.apply(lambda row: row in in_app_purchase)])
accuracy_in_app_purchase = str(round(((valid_in_app_purchase) / total_rows) * 100, 2))
valid_in_app_purchase = str(round(((valid_in_app_purchase) / len(in_app_purchase_clean)) * 100, 2))
validity_list.append(valid_in_app_purchase)
accuracy_list.append(accuracy_in_app_purchase)

# Editor Choice
editor_choice_clean = get_clean_column('Editor Choice')
editor_choice = editor_choice_clean.unique()
valid_editor_choice = len(editor_choice_clean[editor_choice_clean.apply(lambda row: row in editor_choice)])
accuracy_editor_choice = str(round(((valid_editor_choice) / total_rows) * 100, 2))
valid_editor_choice = str(round(((valid_editor_choice) / len(editor_choice_clean)) * 100, 2))
validity_list.append(valid_editor_choice)
accuracy_list.append(accuracy_editor_choice)

# Summary
summary_clean = get_clean_column('Summary')
summary_valid = len(summary_clean[summary_clean.apply(lambda row: re.match(summary_pattern, row) != None)])
accuracy_summary = str(round(((len(summary_clean) - summary_valid) / total_rows) * 100, 2))
summary_valid = str(round(((len(summary_clean) - summary_valid) / len(summary_clean)) * 100, 2))
validity_list.append(summary_valid)
accuracy_list.append(accuracy_summary)

# Reviews
reviews_clean = get_clean_column('Reviews')
reviews_outliers = len(calculate_outliers('Reviews'))
accuracy_reviews = str(round(((len(reviews_clean) - reviews_outliers) / total_rows) * 100, 2))
reviews_outliers = str(round(((len(reviews_clean) - reviews_outliers) / len(reviews_clean)) * 100, 2))
validity_list.append(reviews_outliers)
accuracy_list.append(accuracy_reviews)

# Android version Text
data['Android Ver Edited'] = data['Android version Text'].str.replace(' and up', '')
android_version_clean = get_clean_column('Android Ver Edited')
valid_android_version = len(android_version_clean[android_version_clean.apply(lambda row: (re.match(android_version_pattern, str(row)) != None) | ((str(row) == 'Varies with device')))])
accuracy_android_version = str(round(((valid_android_version) / total_rows) * 100, 2))
valid_android_version = str(round(((valid_android_version) / len(android_version_clean)) * 100, 2))
validity_list.append(valid_android_version)
accuracy_list.append(accuracy_android_version)

# Developer
developer_clean = get_clean_column('Developer')
developer_valid = len(developer_clean[developer_clean.apply(lambda row: re.match(developer_pattern, row) != None)])
accuracy_developer = str(round(((developer_valid) / total_rows) * 100, 2))
developer_valid = str(round(((developer_valid) / len(developer_clean)) * 100, 2))
validity_list.append(developer_valid)
accuracy_list.append(accuracy_developer)

# Developer Address
developer_address_clean = get_clean_column('Developer Address')
developer_address_valid = len(developer_address_clean[developer_address_clean.apply(lambda row: re.match(developer_address_pattern, row) != None)])
accuracy_developer_address = str(round(((len(developer_address_clean) - developer_address_valid) / total_rows) * 100, 2))
developer_address_valid = str(round(((len(developer_address_clean) - developer_address_valid) / len(developer_address_clean)) * 100, 2))
validity_list.append(developer_address_valid)
accuracy_list.append(accuracy_developer_address)

# Developer Internal ID
developer_internal_ID_clean = get_clean_column('Developer Internal ID')
developer_internal_ID_outliers = len(calculate_outliers('Developer Internal ID'))
accuracy_developer_internal_ID = str(round(((len(developer_internal_ID_clean) - developer_internal_ID_outliers) / total_rows) * 100, 2))
developer_internal_ID_outliers = str(round(((len(developer_internal_ID_clean) - developer_internal_ID_outliers) / len(developer_internal_ID_clean)) * 100, 2))
validity_list.append(developer_internal_ID_outliers)
accuracy_list.append(accuracy_developer_internal_ID)

# Version
version_clean = get_clean_column('Version')
list_of_match_versions = version_clean.apply(lambda row: re.match(version_pattern, str(row)) == None)
n = 0
for item in list_of_match_versions:
    if item == True:
        n += 1
accuracy_current_version = str(round(((len(version_clean) - n) / total_rows) * 100, 2))
validity_current_version = str(round(((len(version_clean) - n) / len(version_clean)) * 100, 2))
validity_list.append(validity_current_version)
accuracy_list.append(accuracy_current_version)

# Features Detail
for col in features:
    number_rows.append(total_rows)

df['Completeness'] = completeness_list
df['Currentness'] = currentness_list
df['Consistency'] = consistency_list
df['Validity'] = validity_list
df['Accuracy'] = accuracy_list
df['Total rows'] = total_rows
df['Total nulls'] = number_nulls

print(df.head(29))
    
# print(len(validity_list))
# print(len(currentness_list))
# print(features)