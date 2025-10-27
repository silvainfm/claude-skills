# Polars API Reference

Quick reference for commonly used Polars methods and expressions.

## Reading Data

```python
import polars as pl

# CSV
pl.read_csv('file.csv')
pl.scan_csv('file.csv')  # Lazy

# Parquet
pl.read_parquet('file.parquet')
pl.scan_parquet('file.parquet')  # Lazy

# JSON
pl.read_json('file.json')
pl.read_ndjson('file.jsonl')  # Newline-delimited

# Excel
pl.read_excel('file.xlsx', sheet_name='Sheet1')

# Database
pl.read_database('SELECT * FROM table', connection_uri)
```

## Writing Data

```python
df.write_csv('output.csv')
df.write_parquet('output.parquet')
df.write_json('output.json')
df.write_ndjson('output.jsonl')
df.write_excel('output.xlsx')
```

## Selection and Filtering

```python
# Select columns
df.select(['col1', 'col2'])
df.select([pl.col('col1'), pl.col('col2')])

# Filter rows
df.filter(pl.col('age') > 25)
df.filter((pl.col('age') > 25) & (pl.col('city') == 'NYC'))

# Both
df.select(['name', 'age']).filter(pl.col('age') > 25)
```

## Column Operations

```python
# Add columns
df.with_columns([
    (pl.col('a') + pl.col('b')).alias('sum'),
    pl.col('name').str.to_uppercase().alias('NAME')
])

# Rename
df.rename({'old': 'new'})

# Drop columns
df.drop(['col1', 'col2'])

# Cast types
df.with_columns(pl.col('age').cast(pl.Int32))
```

## Aggregations

```python
# Group by
df.group_by('category').agg([
    pl.col('sales').sum(),
    pl.col('sales').mean(),
    pl.col('sales').count(),
    pl.col('customer').n_unique()
])

# Without grouping
df.select([
    pl.sum('sales'),
    pl.mean('price'),
    pl.median('quantity'),
    pl.std('revenue')
])
```

## Common Expressions

```python
# Numeric
pl.col('price') * 1.1
pl.col('quantity').abs()
pl.col('value').round(2)

# String
pl.col('name').str.to_uppercase()
pl.col('text').str.strip()
pl.col('email').str.contains('@')
pl.col('text').str.replace('old', 'new')
pl.col('name').str.lengths()

# Date/Time
pl.col('date').dt.year()
pl.col('date').dt.month()
pl.col('date').dt.day()
pl.col('timestamp').dt.hour()
pl.col('date').dt.offset_by('1d')

# Conditional
pl.when(pl.col('age') < 18)
    .then(pl.lit('minor'))
    .otherwise(pl.lit('adult'))
```

## Joining

```python
# Inner join
df1.join(df2, on='id', how='inner')

# Left join
df1.join(df2, on='id', how='left')

# Different column names
df1.join(df2, left_on='id', right_on='customer_id')

# Multiple columns
df1.join(df2, on=['col1', 'col2'])
```

## Sorting

```python
# Single column
df.sort('age')
df.sort('salary', descending=True)

# Multiple columns
df.sort(['dept', 'salary'], descending=[False, True])
```

## Window Functions

```python
# Cumulative sum
df.with_columns(pl.col('sales').cum_sum().alias('cumulative'))

# Rolling average
df.with_columns(
    pl.col('price').rolling_mean(window_size=7).alias('7day_avg')
)

# Rank
df.with_columns(
    pl.col('score').rank().over('category').alias('rank')
)

# Shift (lag/lead)
df.with_columns([
    pl.col('value').shift(1).alias('prev'),
    pl.col('value').shift(-1).alias('next')
])
```

## Lazy Evaluation

```python
# Build lazy query
lazy = (
    pl.scan_csv('data.csv')
    .filter(pl.col('active') == True)
    .select(['id', 'name', 'value'])
    .group_by('name')
    .agg(pl.sum('value'))
)

# Execute
result = lazy.collect()

# See plan
print(lazy.explain())
```

## List Operations

```python
# Explode list column
df.explode('tags')

# List length
df.with_columns(pl.col('items').list.len().alias('num_items'))

# List operations
df.with_columns([
    pl.col('numbers').list.sum(),
    pl.col('values').list.mean(),
    pl.col('items').list.first()
])
```

## Null Handling

```python
# Check nulls
df.null_count()

# Fill nulls
df.with_columns(pl.col('age').fill_null(0))

# Drop nulls
df.drop_nulls()
df.drop_nulls(subset=['col1', 'col2'])

# Replace
df.with_columns(
    pl.when(pl.col('value').is_null())
        .then(0)
        .otherwise(pl.col('value'))
)
```

## Data Types

```python
# Common types
pl.Int32, pl.Int64
pl.Float32, pl.Float64
pl.String, pl.Boolean
pl.Date, pl.Datetime
pl.List(pl.String)

# Cast
df.with_columns(pl.col('age').cast(pl.Int32))

# Check schema
df.schema
```

## Performance Methods

```python
# Head/tail
df.head(10)
df.tail(5)

# Sample
df.sample(n=1000)
df.sample(fraction=0.1)

# Describe statistics
df.describe()

# Count rows
df.height
len(df)

# Count columns
df.width
```

## Chaining Example

```python
result = (
    pl.scan_csv('data.csv')
    .filter(pl.col('date') >= '2024-01-01')
    .with_columns([
        pl.col('price').cast(pl.Float64),
        pl.col('quantity').cast(pl.Int32)
    ])
    .with_columns(
        (pl.col('price') * pl.col('quantity')).alias('total')
    )
    .group_by('category')
    .agg([
        pl.sum('total').alias('revenue'),
        pl.count().alias('transactions')
    ])
    .sort('revenue', descending=True)
    .collect()
)
```

## Additional Resources

- Official docs: https://docs.pola.rs/
- API reference: https://docs.pola.rs/api/python/stable/reference/
- User guide: https://docs.pola.rs/user-guide/
