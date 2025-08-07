import pandas as pd
import datetime

df = pd.read_csv('retail_store_sales.csv')

# === 1. Data Cleaning ===

df_cleaned = df.dropna(subset=['Item', 'Price Per Unit', 'Quantity', 'Total Spent'])
df_cleaned = df_cleaned.fillna('False')
df_cleaned = df_cleaned.drop_duplicates(subset=['Transaction ID', 'Transaction Date'])
df_cleaned['Transaction Date'] = pd.to_datetime(df_cleaned['Transaction Date'])

# Анализ и метрики
# Общая выручка на клиента, средний чек
df_total_per_cust = df_cleaned.groupby('Customer ID')['Total Spent'].sum()
df_avg_check_per_cust = df_cleaned.groupby('Customer ID')['Total Spent'].mean().round(2)
df_avg_check_per_categ = df_cleaned.groupby('Category')['Total Spent'].mean().round(2)

# Количество покупок онлайн и оффлайн
df_location = df_cleaned['Location'].value_counts()

# === 2. RFM - recency, frequency, monetary analysis ===

# Recency
Date_now = pd.to_datetime(datetime.datetime.now().date())
last_purchase = df_cleaned.groupby('Customer ID')['Transaction Date'].max()
Recency = (Date_now - last_purchase).dt.days.reset_index(name='Last Purchase Days Left')

# Frequency
Frequency = df_cleaned.groupby('Customer ID')['Transaction ID'].count().reset_index(name='Count Purchases')

# Monetary
Monetary = df_total_per_cust.reset_index()

# Full table
RFM_table = Recency.merge(Frequency, on='Customer ID', how='inner')
RFM_table = RFM_table.merge(Monetary, on='Customer ID', how='inner')
RFM_table = RFM_table.sort_values(by='Last Purchase Days Left')

# === 3. Sales Trends (Top 5) ===

top_5_quantity = df_cleaned.groupby('Item')['Quantity'].sum().sort_values(ascending=False).head(5).reset_index(name='top_5_quantity')
top_5_revenue = df_cleaned.groupby('Item')['Total Spent'].sum().sort_values(ascending=False).head(5).reset_index(name='top_5_revenue')

# Графики топ 5 товаров по выручке и топ 5 товаров по проданному количеству
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(10, 8))
sns.barplot(x='Item', y='top_5_quantity', data=top_5_quantity, hue='Item', legend=False, palette='Purples_r')
plt.xlabel('Товар')
plt.ylabel('Количество продаж')
plt.title('Топ-5 товаров по количеству продаж')
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 8))
sns.barplot(x='Item', y='top_5_revenue', data=top_5_revenue, hue='Item', legend=False, palette='Purples_r')
plt.xlabel('Товар')
plt.ylabel('Выручка')
plt.title('Топ-5 товаров по выручке')
plt.tight_layout()
plt.show()

# === 4. A/B Testing ===

# Условные группы (А - не использовали промокод, В - использовали)
from scipy import stats

# Разделяем на группы
group_A = df_cleaned[df_cleaned['Discount Applied'] == False]['Total Spent']
group_B = df_cleaned[df_cleaned['Discount Applied'] == True]['Total Spent']

# Считаем средний чек
mean_A = group_A.mean()
mean_B = group_B.mean()

# T-test
t_stat, p_value = stats.ttest_ind(group_A, group_B, equal_var=False)

print(f'Средний чек (A): {mean_A:.2f}')
print(f'Средний чек (B): {mean_B:.2f}')
print(f'T-статистика: {t_stat:.4f}')
print(f'P-value: {p_value:.4f}')

# Вывод результата
if p_value < 0.05:
    print('Разница статистически значима — промокод влияет на средний чек.')
else:
    print('Разница незначима — промокод не оказывает влияния на средний чек.')

# Сохранение таблиц для визуализации Power BI
ab_table = pd.DataFrame({
    'Group': ['A (без промо)', 'B (с промо)'],
    'Count': [len(group_A), len(group_B)],
    'Average_Check': [mean_A, mean_B],
    'T_stat': [t_stat, t_stat],
    'P_value': [p_value, p_value]
})

ab_table.to_csv('ab_test_results.csv', index=False)
df_cleaned.to_csv('df_cleaned.csv', index=False)
RFM_table.to_csv('RFM_table.csv', index=False)
top_5_quantity.to_csv('top_5_quantity.csv', index=False)
top_5_revenue.to_csv('top_5_revenue.csv', index=False)