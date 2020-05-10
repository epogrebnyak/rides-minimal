import pandas as pd  # type: ignore

__all__ = ["pairs_dataframe"]


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


def pairs_dataframe(dicts, milages):
    df = pd.DataFrame(dicts)
    df = extend(df, milages)
    return df.sort_values("cov", ascending=False).reset_index(drop=True)
