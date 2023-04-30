import pandas as pd
from models import OpenDataSource


df = pd.read_csv("./NFWBS_PUF_2016_data.csv")


def explore_df():
    print(df.head())
    print()
    print(df.shape)
    print()
    print(df.dtypes)
    print()
    print(df.info())
    print()
    print(df.describe())
    print()
    print(df.columns)
    print()
    print(df.index)


def get_ratio(key):
    filtered_df = df.loc[df["Variable_name"] == key]
    target_df = filtered_df.loc[filtered_df["reaponse_value"] >= 4]
    target_df["unweighted_frequency"] = target_df["unweighted_frequency"].apply(
        lambda x: int(x.replace(",", "")))
    target_count = target_df["unweighted_frequency"].sum()

    filtered_df["unweighted_frequency"] = filtered_df["unweighted_frequency"].apply(
        lambda x: int(x.replace(",", "")))
    total_count = filtered_df["unweighted_frequency"].sum()
    return target_count / total_count


def get_open_data_source():
    return OpenDataSource(
        distress=get_ratio("DISTRESS"),
        control=get_ratio("FWB2_4"),
        frugality=get_ratio("FRUGALITY"),
        skills=get_ratio("FSscore"),
        confident_in_savings=get_ratio("FWB1_6"),
        source="Consumer Financial Protection Bureau"
    )


if __name__ == "__main__":
    explore_df()
    print(get_open_data_source().dict())
