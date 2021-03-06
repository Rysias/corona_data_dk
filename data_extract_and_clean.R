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
    # Filtering out Faroe Islands
    filter(CountryOrRegion == "Denmark" & !ProvinceOrState %in% c("Faroe Islands", "Greenland")) %>% 
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
confirmed_url <- "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
confirmed_data <- get_clean_data(confirmed_url, case_type="confirmed")

deceased_url <- "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
deceased_data <- get_clean_data(deceased_url, case_type="deceased")

recovered_url <- "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"
recovered_data <- get_clean_data(recovered_url, case_type="recovered")

combined_df <- confirmed_data %>% 
  left_join(deceased_data, by="date") %>% 
  left_join(recovered_data, by="date") %>% 
  filter(confirmed > 0)

write_csv(combined_df, "corona_data_dk.csv")