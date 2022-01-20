def cleanDF(df):
    df = df[df.iloc[0].dropna().index]
    rows_with_nan = []
    for index, row in df.iterrows():
            is_nan_series = row.isnull()
            if is_nan_series.any():
                    rows_with_nan.append(index)
            
    for row in rows_with_nan:
            df.drop(row, inplace=True)

    return df

def dropEmptyColumns(df):
    df = df[df.iloc[0].dropna().index]
    return df