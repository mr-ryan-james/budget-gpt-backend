import pandas as pd
from models import OpenDataSource


df = pd.read_csv("./NFWBS_PUF_2016_data.csv")


def explore_df():
    print(df.head())
    print(df.dtypes)
    print(df.info())
    print(df.describe())
    print(df.columns)
    print(df.index)


def get_distress_ratio():
    distress_count = df.loc[df["DISTRESS"] >= 4].shape[0]
    return distress_count / df.shape[0]


def get_control_ratio():
    control_count = df.loc[df["FWB2_4"] >= 4].shape[0]
    return control_count / df.shape[0]


def get_frugality_ratio():
    frugality_count = df.loc[df["FRUGALITY"] >= 4].shape[0]
    return frugality_count / df.shape[0]


def get_skills_ratio():
    skills_count = df.loc[df["FSscore"] >= 68].shape[0]
    return skills_count / df.shape[0]


def get_confident_in_savings_ratio():
    confidence_count = df.loc[df["FWB1_6"] >= 4].shape[0]
    return confidence_count / df.shape[0]


def get_open_data_source():
    return OpenDataSource(
        distress=get_distress_ratio(),
        control=get_control_ratio(),
        frugality=get_frugality_ratio(),
        skills=get_skills_ratio(),
        confident_in_savings=get_confident_in_savings_ratio(),
        source="Consumer Financial Protection Bureau"
    )


if __name__ == "__main__":
    explore_df()
