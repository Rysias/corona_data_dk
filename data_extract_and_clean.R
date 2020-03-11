##################################
# DATA EXTRACTION AND FORMATTING #
##################################


# Loading libraries
library(tidyverse)
library(RCurl)

# Helper functions
clean_data <- function(df, case_type) {
  df %>% 
    rename(CountryOrRegion = "Country/Region", 
           ProvinceOrState = "Province/State") %>%
    filter(CountryOrRegion == "Denmark") %>% 
    # Select all the columns with dates
    select(matches("\\d")) %>% 
    gather(key = date, value = !!as.symbol(case_type)) %>% 
    # Format date
    mutate(date = paste(date, "20", sep=""),
           date = as.Date(date, format = "%m/%d/%Y"))
}


data_from_url <- function(data_url) {
  raw_text <- getURL(data_url)
  read_csv(raw_text)
}


get_clean_data <- function(data_url, case_type = "confirmed") {
  raw_data <- data_from_url(data_url)
  clean_data(raw_data, case_type)
}


# Getting the data
confirmed_url <- "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
confirmed_data <- get_clean_data(confirmed_url, case_type="confirmed")

deceased_url <- "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv"
deceased_data <- get_clean_data(deceased_url, case_type="deceased")

combined_df <- confirmed_data %>% 
  left_join(deceased_data, by="date") %>% 
  filter(confirmed > 0)




