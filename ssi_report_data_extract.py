# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 08:57:12 2020

@author: jry
"""
import camelot
import pandas as pd
import sys
from datetime import datetime
from urllib import error


def get_data_tables():
    formatted_date = DATE.strftime("%d%m%Y")
    daily_url = f"https://files.ssi.dk/COVID19-overvaagningsrapport-{formatted_date}"
    try:
        return camelot.read_pdf(daily_url, pages="all")
    except error.HTTPError:
        try:
            new_daily_url = f"https://www.ssi.dk/-/media/arkiv/dk/aktuelt/sygdomsudbrud/covid19-rapport/covid19-overvaagningsrapport-{formatted_date}.pdf?la=da"
            return camelot.read_pdf(new_daily_url, pages="all")
        except error.HTTPError:
            print("no article for the day")
            sys.exit()


def table_header(table_df):
    try:
        return table_df.loc[0, 0]
    except TypeError:
        return ""



def is_ages(table_df):
    return table_header(table_df).startswith("Aldersgrupper \nLaboratorieb")


def is_regional(table_df):
    return table_header(table_df).startswith("Landsdel \nLaboratorieb") and \
            table_df.loc[1, 0] == "København by"


def get_df(type_func):
    """
    gets a certain df based on the type function (that should
    return a bool)
    """
    return next(table.df.copy() for table in ALL_TABLES if
                type_func(table.df))


def set_column_names(df):
    new_df = df.copy()
    col_names = new_df.loc[0, 0].split(" \n")
    new_df.columns = col_names
    return new_df


def reorder_columns(df):
    """ puts date first """
    cols = df.columns.tolist()
    new_cols = cols[-1:] + cols[:-1]
    return df[new_cols]


def add_date(df):
    """ for I/O stuff it makes more sense to keep date as a string """
    date_col = DATE.strftime("%Y-%m-%d")
    return reorder_columns(df.assign(date=date_col))


def get_clean_regional():
    df = get_df(is_regional)
    # setting col_names
    regional_colnames = ["region", "confirmed", "population", "X"]
    df.columns = regional_colnames
    # filtering out totals and junk rows (0, 11)
    df = df.loc[range(1, 11)].reset_index().drop(["X", "index"], axis=1)
    # add date
    df["date"] = DATE

    # clean datatypes
    clean_int_cols(df, ["confirmed", "population"])

    return add_date(df)


def clean_int_cols(df, int_cols):
    """ fixes the dtype of those pesky "."-thousand seperators! """
    df[int_cols] = df[int_cols].astype("object") \
                               .replace("\.", "", regex=True) \
                               .astype("int32")


def get_clean_age():
    """
    Removes aggregate rows and columns, renames columns and converts data types
    """
    df = get_df(is_ages)

    # set col_names
    age_colnames = ["ageGroup", "confirmed", "tested", "X"]
    df.columns = age_colnames

    # filtering out totals and junk rows (0, 11)
    df = df.loc[range(1, 11)].reset_index().drop(["X", "index"], axis=1)

    # cleaning dtypes
    clean_int_cols(df, ["confirmed", "tested"])
    return add_date(df)


def is_hospital(table_df):
    return table_header(table_df).startswith("Antal \nHeraf indlagte \n")


def fix_newline(df, col_name):
    """
    fixes an annoying problem where a row consists of new-lines in
    the first columns instead of a value per column
    """
    problem_rows = df[col_name].str.contains("\n")
    fixed_rows = df.loc[problem_rows, col_name].str.split("\n").to_list()
    joined_df = pd.concat((df[~problem_rows],
                           pd.DataFrame(fixed_rows, columns=df.columns)))
    return joined_df.reset_index(drop=True)


def get_clean_hospital():
    """ gets the table of hospital cases per region """
    df = get_df(is_hospital)

    # set col_names
    hospital_colnames = ["region", "hospitalized", "intensive_care",
                         "in_ventilation"]
    df.columns = hospital_colnames


    # filtering out totals and junk rows
    df = df.loc[range(1, 6)].reset_index(drop=True)

    # Fixing newline bug
    df = fix_newline(df, "region")

    # cleaning dtypes
    clean_int_cols(df, ["hospitalized", "intensive_care", "in_ventilation"])
    return add_date(df)


def current_date():
    return datetime.now().date()


def concat_and_write(df, df_type="regional"):
    try:
        old_df = pd.read_csv(f"corona_{df_type}_data.csv")
    except FileNotFoundError:
        df.to_csv(f"corona_{df_type}_data.csv", index=False)
        return ""
    combined = pd.concat([old_df, df]).drop_duplicates().sort_values(["date"])
    combined.to_csv(f"corona_{df_type}_data.csv", index=False)


# Setting the date
DATE = current_date()
DATE = datetime(2020, 3, 21).date()

print("Reading the report of the day...")
ALL_TABLES = get_data_tables()
print("done!")

age_df = get_clean_age()
regional_df = get_clean_regional()
hospitalized_df = get_clean_hospital()

print("writing data")
# Adding to the old data
concat_and_write(regional_df, df_type="regional")
concat_and_write(age_df, df_type="age")
concat_and_write(hospitalized_df, df_type="hospitalized")
print("done!")
