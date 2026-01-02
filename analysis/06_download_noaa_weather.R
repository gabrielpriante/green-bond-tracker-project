#!/usr/bin/env Rscript
# analysis/06_download_noaa_weather.R
#
# NOAA Weather Data Download and Processing
# 
# Purpose:
#   Download GHCN-Daily weather data for selected station(s) and produce
#   clean, analysis-ready daily weather outputs with QA flags.
#
# Inputs:
#   - data/context/noaa_weather_config.yml (configuration from station selection)
#
# Outputs:
#   - data/raw/noaa/ghcnd_primary_YYYYMMDD.csv (raw primary station data)
#   - data/raw/noaa/ghcnd_backup_YYYYMMDD.csv (raw backup station data, if used)
#   - data/processed/noaa_daily_weather.csv (cleaned daily weather data)
#   - data/context/noaa_weather_qc_summary.csv (QC summary statistics)
#   - docs/noaa_weather_data_dictionary.md (data dictionary)
#
# Usage:
#   Rscript analysis/06_download_noaa_weather.R
#   or source("analysis/06_download_noaa_weather.R")

# Load required libraries
suppressPackageStartupMessages({
  library(tidyverse)
  library(rnoaa)
  library(yaml)
  library(lubridate)
})

cat("=== NOAA WEATHER DATA DOWNLOAD & PROCESSING ===\n\n")

# Configuration
CONFIG_PATH <- "data/context/noaa_weather_config.yml"
OUTPUT_PROCESSED_PATH <- "data/processed/noaa_daily_weather.csv"
OUTPUT_QC_PATH <- "data/context/noaa_weather_qc_summary.csv"
OUTPUT_DOC_PATH <- "docs/noaa_weather_data_dictionary.md"
RAW_DATA_DIR <- "data/raw/noaa"

# QC thresholds
MAX_MISSING_THRESHOLD <- 0.10  # Use backup if >10% missing
EXTREME_TEMP_MIN_C <- -60  # Extreme cold threshold
EXTREME_TEMP_MAX_C <- 60   # Extreme heat threshold

# Helper function: Convert GHCN-Daily PRCP to mm
convert_prcp_to_mm <- function(prcp_tenths_mm) {
  # GHCN-Daily PRCP is in tenths of mm
  prcp_tenths_mm / 10
}

# Helper function: Convert GHCN-Daily temperature to Celsius
convert_temp_to_celsius <- function(temp_tenths_c) {
  # GHCN-Daily TMAX/TMIN are in tenths of degrees C
  temp_tenths_c / 10
}

# Helper function: Download station data
download_station_data <- function(station_id, start_date, end_date, token = NULL) {
  cat(sprintf("  Downloading data for %s...\n", station_id))
  
  all_data <- list()
  
  # Download each variable separately (GHCN-Daily requirement)
  for (var in c("PRCP", "TMAX", "TMIN")) {
    tryCatch({
      data <- ncdc(
        datasetid = "GHCND",
        stationid = station_id,
        datatypeid = var,
        startdate = start_date,
        enddate = end_date,
        limit = 1000,  # Max per request
        token = token
      )
      
      if (!is.null(data) && nrow(data$data) > 0) {
        all_data[[var]] <- data$data %>%
          select(date, datatype, value) %>%
          mutate(date = as.Date(date))
      }
      
      # Rate limiting (NOAA API)
      Sys.sleep(0.2)
      
    }, error = function(e) {
      cat(sprintf("    ! Warning: Could not fetch %s: %s\n", var, conditionMessage(e)))
    })
  }
  
  if (length(all_data) == 0) {
    return(NULL)
  }
  
  # Combine variables into wide format
  combined <- bind_rows(all_data) %>%
    pivot_wider(names_from = datatype, values_from = value, values_fn = mean)
  
  return(combined)
}

# STEP 1: Read and validate configuration
cat("STEP 1: Reading configuration...\n")

if (!file.exists(CONFIG_PATH)) {
  stop(paste0(
    "ERROR: Configuration file not found at ", CONFIG_PATH, "\n",
    "Please run analysis/05_select_noaa_station.R first."
  ))
}

config <- read_yaml(CONFIG_PATH)

# Validate required fields
required_fields <- c("time_period", "stations", "variables")
missing_fields <- setdiff(required_fields, names(config))

if (length(missing_fields) > 0) {
  stop(paste0(
    "ERROR: Configuration missing required fields: ",
    paste(missing_fields, collapse = ", ")
  ))
}

start_date <- as.Date(config$time_period$start_date)
end_date <- as.Date(config$time_period$end_date)
primary_id <- config$stations$primary$id
backup_id <- config$stations$backup$id

cat(sprintf("  ✓ Period: %s to %s\n", start_date, end_date))
cat(sprintf("  ✓ Primary station: %s\n", primary_id))
cat(sprintf("  ✓ Backup station: %s\n", backup_id))

# Check for NOAA API token
noaa_token <- Sys.getenv("NOAA_TOKEN", unset = NA)
if (is.na(noaa_token)) {
  cat("\n  ! WARNING: NOAA_TOKEN not set. API calls may be rate-limited.\n")
  cat("  ! Get a free token at: https://www.ncdc.noaa.gov/cdo-web/token\n\n")
  noaa_token <- NULL
} else {
  cat("  ✓ NOAA API token found\n")
}

# STEP 2: Download primary station data
cat("\nSTEP 2: Downloading primary station data...\n")

primary_data <- download_station_data(
  primary_id,
  format(start_date, "%Y-%m-%d"),
  format(end_date, "%Y-%m-%d"),
  noaa_token
)

if (is.null(primary_data)) {
  stop("ERROR: Failed to download primary station data.")
}

cat(sprintf("  ✓ Downloaded %d observations from primary station\n", nrow(primary_data)))

# Save raw primary data
primary_raw_file <- file.path(
  RAW_DATA_DIR,
  sprintf("ghcnd_primary_%s.csv", format(Sys.Date(), "%Y%m%d"))
)

if (!dir.exists(RAW_DATA_DIR)) {
  dir.create(RAW_DATA_DIR, recursive = TRUE)
}

write_csv(primary_data, primary_raw_file)
cat(sprintf("  ✓ Saved raw data: %s\n", primary_raw_file))

# STEP 3: Assess primary data quality
cat("\nSTEP 3: Assessing data quality...\n")

# Create complete daily sequence
all_dates <- data.frame(
  date = seq(start_date, end_date, by = "day")
)

# Merge with observations
primary_full <- all_dates %>%
  left_join(primary_data, by = "date")

# Calculate missingness
missing_prcp <- sum(is.na(primary_full$PRCP)) / nrow(primary_full)
missing_tmax <- sum(is.na(primary_full$TMAX)) / nrow(primary_full)
missing_tmin <- sum(is.na(primary_full$TMIN)) / nrow(primary_full)

cat(sprintf("  Missing data rates:\n"))
cat(sprintf("    PRCP: %.1f%%\n", missing_prcp * 100))
cat(sprintf("    TMAX: %.1f%%\n", missing_tmax * 100))
cat(sprintf("    TMIN: %.1f%%\n", missing_tmin * 100))

# STEP 4: Download backup station if needed
use_backup <- any(c(missing_prcp, missing_tmax, missing_tmin) > MAX_MISSING_THRESHOLD)
backup_data <- NULL

if (use_backup && primary_id != backup_id) {
  cat("\n  ! High missingness detected. Downloading backup station...\n")
  
  backup_data <- download_station_data(
    backup_id,
    format(start_date, "%Y-%m-%d"),
    format(end_date, "%Y-%m-%d"),
    noaa_token
  )
  
  if (!is.null(backup_data)) {
    cat(sprintf("  ✓ Downloaded %d observations from backup station\n", nrow(backup_data)))
    
    # Save raw backup data
    backup_raw_file <- file.path(
      RAW_DATA_DIR,
      sprintf("ghcnd_backup_%s.csv", format(Sys.Date(), "%Y%m%d"))
    )
    write_csv(backup_data, backup_raw_file)
    cat(sprintf("  ✓ Saved raw data: %s\n", backup_raw_file))
  } else {
    cat("  ! Warning: Could not download backup station data\n")
  }
}

# STEP 5: Clean and merge data
cat("\nSTEP 5: Cleaning and standardizing data...\n")

# Start with primary station
weather <- primary_full %>%
  mutate(
    source_station_id = primary_id,
    source_notes = "primary"
  )

# Fill gaps with backup if available
if (!is.null(backup_data) && nrow(backup_data) > 0) {
  backup_full <- all_dates %>%
    left_join(backup_data, by = "date")
  
  # Fill missing values
  filled_count <- 0
  for (i in 1:nrow(weather)) {
    if (is.na(weather$PRCP[i]) && !is.na(backup_full$PRCP[i])) {
      weather$PRCP[i] <- backup_full$PRCP[i]
      weather$source_station_id[i] <- backup_id
      weather$source_notes[i] <- "backup_prcp"
      filled_count <- filled_count + 1
    }
    if (is.na(weather$TMAX[i]) && !is.na(backup_full$TMAX[i])) {
      weather$TMAX[i] <- backup_full$TMAX[i]
      if (weather$source_notes[i] == "primary") {
        weather$source_station_id[i] <- backup_id
        weather$source_notes[i] <- "backup_tmax"
      } else {
        weather$source_notes[i] <- paste0(weather$source_notes[i], "+tmax")
      }
      filled_count <- filled_count + 1
    }
    if (is.na(weather$TMIN[i]) && !is.na(backup_full$TMIN[i])) {
      weather$TMIN[i] <- backup_full$TMIN[i]
      if (weather$source_notes[i] == "primary") {
        weather$source_station_id[i] <- backup_id
        weather$source_notes[i] <- "backup_tmin"
      } else {
        weather$source_notes[i] <- paste0(weather$source_notes[i], "+tmin")
      }
      filled_count <- filled_count + 1
    }
  }
  
  cat(sprintf("  ✓ Filled %d missing values from backup station\n", filled_count))
}

# Convert units
weather <- weather %>%
  mutate(
    precipitation_mm = convert_prcp_to_mm(PRCP),
    tmax_c = convert_temp_to_celsius(TMAX),
    tmin_c = convert_temp_to_celsius(TMIN)
  )

# Calculate mean temperature
weather <- weather %>%
  mutate(
    tmean_c = case_when(
      !is.na(tmax_c) & !is.na(tmin_c) ~ (tmax_c + tmin_c) / 2,
      TRUE ~ NA_real_
    )
  )

cat("  ✓ Unit conversions complete\n")

# STEP 6: Apply QA/QC flags
cat("\nSTEP 6: Applying quality control flags...\n")

weather <- weather %>%
  mutate(
    # Flag missing core variables
    flag_missing_prcp = is.na(precipitation_mm),
    flag_missing_tmax = is.na(tmax_c),
    flag_missing_tmin = is.na(tmin_c),
    
    # Flag invalid values
    flag_invalid_prcp = !is.na(precipitation_mm) & precipitation_mm < 0,
    flag_invalid_temp_order = !is.na(tmax_c) & !is.na(tmin_c) & tmax_c < tmin_c,
    
    # Flag extreme temperatures
    flag_extreme_cold = !is.na(tmin_c) & tmin_c < EXTREME_TEMP_MIN_C,
    flag_extreme_heat = !is.na(tmax_c) & tmax_c > EXTREME_TEMP_MAX_C,
    
    # Composite QA flag
    data_quality_flag = case_when(
      flag_invalid_prcp | flag_invalid_temp_order ~ "INVALID",
      flag_missing_prcp & flag_missing_tmax & flag_missing_tmin ~ "MISSING_ALL",
      flag_missing_prcp | flag_missing_tmax | flag_missing_tmin ~ "PARTIAL",
      source_notes != "primary" ~ "FILLED_FROM_BACKUP",
      flag_extreme_cold | flag_extreme_heat ~ "EXTREME",
      TRUE ~ "OK"
    )
  )

# Count flags
flag_counts <- weather %>%
  count(data_quality_flag) %>%
  arrange(desc(n))

cat("  Quality flag distribution:\n")
for (i in 1:nrow(flag_counts)) {
  cat(sprintf("    %s: %d (%.1f%%)\n", 
              flag_counts$data_quality_flag[i], 
              flag_counts$n[i],
              flag_counts$n[i] / nrow(weather) * 100))
}

# STEP 7: Prepare final output
cat("\nSTEP 7: Preparing final output...\n")

weather_final <- weather %>%
  select(
    date,
    precipitation_mm,
    tmax_c,
    tmin_c,
    tmean_c,
    data_quality_flag,
    source_station_id,
    source_notes
  ) %>%
  arrange(date)

write_csv(weather_final, OUTPUT_PROCESSED_PATH)
cat(sprintf("  ✓ Saved processed weather data: %s\n", OUTPUT_PROCESSED_PATH))
cat(sprintf("    Total records: %d\n", nrow(weather_final)))

# STEP 8: Generate QC summary
cat("\nSTEP 8: Generating QC summary...\n")

qc_summary <- tibble(
  metric = c(
    "total_days",
    "start_date",
    "end_date",
    "missing_prcp_pct",
    "missing_tmax_pct",
    "missing_tmin_pct",
    "missing_tmean_pct",
    "invalid_records",
    "extreme_records",
    "backup_filled_records",
    "ok_records",
    "primary_station_id",
    "backup_station_id",
    "backup_used"
  ),
  value = c(
    as.character(nrow(weather_final)),
    as.character(min(weather_final$date)),
    as.character(max(weather_final$date)),
    sprintf("%.2f", sum(is.na(weather_final$precipitation_mm)) / nrow(weather_final) * 100),
    sprintf("%.2f", sum(is.na(weather_final$tmax_c)) / nrow(weather_final) * 100),
    sprintf("%.2f", sum(is.na(weather_final$tmin_c)) / nrow(weather_final) * 100),
    sprintf("%.2f", sum(is.na(weather_final$tmean_c)) / nrow(weather_final) * 100),
    as.character(sum(weather_final$data_quality_flag == "INVALID")),
    as.character(sum(weather_final$data_quality_flag == "EXTREME")),
    as.character(sum(grepl("backup", weather_final$source_notes))),
    as.character(sum(weather_final$data_quality_flag == "OK")),
    primary_id,
    backup_id,
    as.character(use_backup)
  )
)

write_csv(qc_summary, OUTPUT_QC_PATH)
cat(sprintf("  ✓ Saved QC summary: %s\n", OUTPUT_QC_PATH))

# STEP 9: Generate data dictionary
cat("\nSTEP 9: Generating data dictionary...\n")

dict_content <- sprintf("# NOAA Weather Data Dictionary

## Overview

This document describes the processed NOAA weather data fields, units, quality control flags, and data sources.

**Generated:** %s  
**Data source:** NOAA GHCN-Daily (Global Historical Climatology Network - Daily)  
**Processing script:** `analysis/06_download_noaa_weather.R`

## File Information

**File:** `data/processed/noaa_daily_weather.csv`  
**Format:** CSV (comma-separated values)  
**Temporal coverage:** %s to %s (%d days)  
**Primary station:** %s  
**Backup station:** %s  

## Field Definitions

### Core Fields

| Field | Type | Unit | Description | Missing Values |
|-------|------|------|-------------|----------------|
| `date` | Date | - | Observation date (YYYY-MM-DD) | None (complete sequence) |
| `precipitation_mm` | Numeric | mm | Daily total precipitation in millimeters | Allowed (flagged) |
| `tmax_c` | Numeric | °C | Daily maximum temperature in degrees Celsius | Allowed (flagged) |
| `tmin_c` | Numeric | °C | Daily minimum temperature in degrees Celsius | Allowed (flagged) |
| `tmean_c` | Numeric | °C | Daily mean temperature: (tmax + tmin) / 2 | Allowed (computed when tmax & tmin exist) |

### Quality Control Fields

| Field | Type | Description |
|-------|------|-------------|
| `data_quality_flag` | Character | Overall quality assessment (see below) |
| `source_station_id` | Character | GHCN-Daily station ID that provided the data for this row |
| `source_notes` | Character | Provenance notes (primary, backup_prcp, backup_tmax, etc.) |

## Data Quality Flags

The `data_quality_flag` field uses the following categories (mutually exclusive, prioritized):

| Flag | Description | Recommended Action |
|------|-------------|-------------------|
| `OK` | All core variables present, no issues detected | Use without restriction |
| `EXTREME` | Temperature outside plausible bounds (<%d°C or >%d°C) | Review before use; likely valid but unusual |
| `FILLED_FROM_BACKUP` | One or more variables filled from backup station | Use with awareness of spatial difference |
| `PARTIAL` | One or more core variables missing | Use available variables; note gaps |
| `MISSING_ALL` | All core variables missing | Exclude from analysis or interpolate |
| `INVALID` | Invalid values detected (PRCP<0 or TMAX<TMIN) | Exclude from analysis |

## Unit Conversions

GHCN-Daily data is stored in tenths of the final unit. This script applies the following conversions:

- **Precipitation:** Raw value (tenths of mm) ÷ 10 → mm
- **Temperature:** Raw value (tenths of °C) ÷ 10 → °C

Example:
- Raw PRCP = 125 → 12.5 mm
- Raw TMAX = 283 → 28.3°C

## Backup Station Gap Filling

When the primary station has >10%% missing data for any core variable, the backup station is used to fill gaps:

1. Missing values in primary station are filled with backup station values for the same date
2. `source_station_id` is updated to reflect the backup station for that row
3. `source_notes` indicates which variables came from backup (e.g., \"backup_prcp\", \"backup_tmax+tmin\")
4. `data_quality_flag` is set to `FILLED_FROM_BACKUP`

**Backup used:** %s

## Data Quality Summary

%s

## Missing Data Patterns

%s

## Known Limitations

1. **Spatial representativeness:** Weather station may be several km from sensor locations
2. **Temporal resolution:** Daily aggregates may miss sub-daily extremes
3. **Sensor changes:** GHCN stations may have instrument or location changes over time
4. **Missing observations:** Even high-quality stations have occasional gaps
5. **Backup filling:** Introduces spatial discontinuity when backup station is used

## Quality Control Thresholds

- **Extreme cold:** < %d°C (flagged but retained)
- **Extreme heat:** > %d°C (flagged but retained)
- **Invalid PRCP:** < 0 mm (flagged as INVALID)
- **Invalid TMAX/TMIN:** TMAX < TMIN (flagged as INVALID)
- **Backup trigger:** > 10%% missing for any core variable

## Usage Recommendations

### For Event Attribution
- Filter to `data_quality_flag %in% c('OK', 'EXTREME', 'FILLED_FROM_BACKUP')`
- Be cautious with `EXTREME` days; validate against other sources
- Document spatial offset between weather station and sensors

### For Time Series Analysis
- Handle `PARTIAL` and `MISSING_ALL` carefully (e.g., interpolation, exclusion)
- Check for systematic gaps (e.g., seasonal instrument outages)
- Consider smoothing to reduce day-to-day noise

### For Regression / Modeling
- Use `OK` and `FILLED_FROM_BACKUP` flags
- Consider lagged effects (e.g., yesterday's precipitation)
- Include `source_station_id` as a random effect if backup is heavily used

## Source Data

- **Dataset:** NOAA GHCN-Daily
- **Access:** NOAA NCEI API (https://www.ncdc.noaa.gov/cdo-web/webservices/v2)
- **Citation:** Menne, M.J., I. Durre, R.S. Vose, B.E. Gleason, and T.G. Houston, 2012: An overview of the Global Historical Climatology Network-Daily Database. Journal of Atmospheric and Oceanic Technology, 29, 897-910. https://doi.org/10.1175/JTECH-D-11-00103.1

## Reproducibility

To reproduce this dataset:

1. Ensure NOAA API token is set: `Sys.setenv(NOAA_TOKEN = 'your_token')`
2. Run station selection: `source('analysis/05_select_noaa_station.R')`
3. Run data download: `source('analysis/06_download_noaa_weather.R')`

Raw data is preserved in `data/raw/noaa/` for transparency.

## Contact

For questions about this dataset or processing methodology, please refer to the project README or open an issue on GitHub.

---

**Last updated:** %s
",
  format(Sys.time(), "%Y-%m-%d %H:%M:%S %Z"),
  min(weather_final$date), max(weather_final$date), nrow(weather_final),
  config$stations$primary$id,
  config$stations$backup$id,
  EXTREME_TEMP_MIN_C, EXTREME_TEMP_MAX_C,
  ifelse(use_backup, "Yes", "No"),
  paste(capture.output(print(qc_summary, n = Inf)), collapse = "\n"),
  sprintf("- Total days: %d\n- Days with complete data (OK): %d (%.1f%%)\n- Days with any missing core variable: %d (%.1f%%)",
          nrow(weather_final),
          sum(weather_final$data_quality_flag == "OK"),
          sum(weather_final$data_quality_flag == "OK") / nrow(weather_final) * 100,
          sum(weather_final$data_quality_flag %in% c("PARTIAL", "MISSING_ALL")),
          sum(weather_final$data_quality_flag %in% c("PARTIAL", "MISSING_ALL")) / nrow(weather_final) * 100),
  EXTREME_TEMP_MIN_C, EXTREME_TEMP_MAX_C,
  format(Sys.time(), "%Y-%m-%d %H:%M:%S %Z")
)

writeLines(dict_content, OUTPUT_DOC_PATH)
cat(sprintf("  ✓ Saved data dictionary: %s\n", OUTPUT_DOC_PATH))

cat("\n=== WEATHER DATA PROCESSING COMPLETE ===\n\n")

cat("Summary:\n")
cat(sprintf("  - Total days processed: %d\n", nrow(weather_final)))
cat(sprintf("  - Date range: %s to %s\n", min(weather_final$date), max(weather_final$date)))
cat(sprintf("  - Records with OK quality: %d (%.1f%%)\n", 
            sum(weather_final$data_quality_flag == "OK"),
            sum(weather_final$data_quality_flag == "OK") / nrow(weather_final) * 100))
cat(sprintf("  - Missing PRCP: %.1f%%\n", sum(is.na(weather_final$precipitation_mm)) / nrow(weather_final) * 100))
cat(sprintf("  - Missing TMAX: %.1f%%\n", sum(is.na(weather_final$tmax_c)) / nrow(weather_final) * 100))
cat(sprintf("  - Missing TMIN: %.1f%%\n", sum(is.na(weather_final$tmin_c)) / nrow(weather_final) * 100))

cat("\nOutputs:\n")
cat(sprintf("  ✓ %s\n", OUTPUT_PROCESSED_PATH))
cat(sprintf("  ✓ %s\n", OUTPUT_QC_PATH))
cat(sprintf("  ✓ %s\n", OUTPUT_DOC_PATH))

cat("\nNext steps:\n")
cat("  - Review QC summary and data dictionary\n")
cat("  - Integrate weather data with sensor observations for event attribution\n\n")
