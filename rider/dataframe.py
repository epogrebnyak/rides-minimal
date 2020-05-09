import pandas as pd

__all__ = ["get_dataframe", "subset"]


def get_date(df):
    return df.time.apply(lambda x: pd.Timestamp(x, unit="s").date().__str__())


def get_dataframe(filename, **kwargs):
    df_full = pd.read_csv(filename, usecols=["car", "time", "lat", "lon"], **kwargs)
    df_full["date"] = get_date(df_full)
    return df_full[["car", "date", "time", "lat", "lon"]]


def subset_by_dates(df, days:[str]):
    ix = df.date.isin(days)
    return df[ix]

def subset_by_vehicle_types(df, types:[str], vehicle_type_resolver):
    ix = df.car.apply(vehicle_type_resolver).isin(types)
    return df[ix]

def subset(df, days, types, vehicle_type_resolver):
    """
    Выбираем из фрейма *df* треки по дням и типам машин. 
    """
    res_ = subset_by_dates(df, days)
    return subset_by_vehicle_types(res_, types, vehicle_type_resolver)


def overlap(df):
    return (
        (df.cov_1 * df.len_1 + df.cov_2 * df.len_2).divide(df.len_1 + df.len_2).round(2)
    )


def extend(df, milages):
    km = lambda i: milages[i]
    df["cov"] = df.cov_1 + df.cov_2
    df["len_1"] = df.id_1.apply(km)
    df["len_2"] = df.id_2.apply(km)
    df["op"] = overlap(df)
    return df


def result_dataframe(dicts, milages):
    df = pd.DataFrame(dicts)
    df = extend(df, milages)
    return df.sort_values("cov", ascending=False).reset_index(drop=True)
