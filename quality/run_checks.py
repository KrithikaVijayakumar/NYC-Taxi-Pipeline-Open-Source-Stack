import pandas as pd

def validate_silver():
    print('Running data quality checks...')
    df = pd.read_parquet('/tmp/silver.parquet')
    errors = []

    if len(df) == 0:
        errors.append('FAIL: No rows in silver dataset')
    else:
        print(f'PASS: Row count = {len(df):,}')

    key_cols = ['lpep_pickup_datetime', 'lpep_dropoff_datetime', 'total_amount']
    for col in key_cols:
        if col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                errors.append(f'FAIL: {null_count} nulls in {col}')
            else:
                print(f'PASS: No nulls in {col}')

    bad_fares = (df['fare_amount'] <= 0).sum()
    if bad_fares > 0:
        errors.append(f'FAIL: {bad_fares} rows with fare_amount <= 0')
    else:
        print(f'PASS: All fare_amount values > 0')

    bad_distance = ((df['trip_distance'] < 0) | (df['trip_distance'] > 100)).sum()
    if bad_distance > 0:
        errors.append(f'FAIL: {bad_distance} rows with invalid trip_distance')
    else:
        print(f'PASS: All trip_distance values valid')

    print(f'\n=== Quality Check Summary ===')
    print(f'Total rows: {len(df):,}')
    print(f'Checks passed: {4 - len(errors)}/4')

    if errors:
        for e in errors:
            print(e)
        raise ValueError(f'Data quality checks failed!')

    print('All quality checks passed!')