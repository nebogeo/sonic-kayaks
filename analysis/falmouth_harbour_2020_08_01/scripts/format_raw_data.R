# Wrangle raw data from sonic kayaks and create plot ready spatial data

# strimas.com/post/hexagonal-grids/

# James P. Duffy - 2020
# james.philip.duffy@gmail.com

#### Setup ####

library(readr)
library(lubridate)
library(tidyr)
library(dplyr)
library(sf)
library(purrr)

detach("package:raster")

hex_size <- 50

bng_epsg <- 27700

# column names
scn <- c("date", "time", "temp", "pm_running", "temp_error", "pm_error", "pm_id", 
         "pm_frame_len", "pm_std_1_0", "pm_std_2_5", "pm_std_10_0", "pm_env_1_0", 
         "pm_env_2_5", "pm_env_10_0", "pm_np_0_1", "pm_np_0_5", "pm_np_1_0", 
         "pm_np_2_5", "pm_np_5_0", "pm_np_10_0", "pm_res", "pm_checksum", 
         "turbid_raw", "turbid_filt_1", "turbid_filt_2", "turbid_filt_3", 
         "turbid_filt_4", "turbid_filt_5", "turbid_filt_6", "turbid_filt_7",
         "blank")

# column names
gpscn <- c("date", "time", "latitude", "longitude", "altitude", "num_sats",
           "hdop", "qi", "code")

#### Processing ####

# read in and format sensor and GNSS data from 3 kayaks

sk1 <- read_csv("raw_data/sk1/sensors.csv", col_names = scn) %>%
  unite(., date_time, date, time, sep = " ") %>%
  mutate(., date_time = ymd_hms(date_time)) %>%
  mutate(across(scn[3:length(scn)], as.numeric))

sk1_gps <- read_csv("raw_data/sk1/adv_gps.log", col_names = gpscn) %>%
  unite(., date_time, date, time, sep = " ") %>%
  mutate(., date_time = ymd_hms(date_time)) %>%
  filter(., code == "FIX") %>%
  select(date_time, latitude, longitude)

# join data
sk1_comb_bng <- left_join(sk1_gps, sk1) %>%
  st_as_sf(., coords = c("longitude", "latitude"), crs = 4326) %>%
  filter(., !between(date_time, as_datetime("2020-07-29 09:46:57"), 
                     as_datetime("2020-07-29 10:24:30"))) %>%
  filter(., !between(date_time, as_datetime("2020-07-29 13:09:00"), 
                     as_datetime("2020-07-29 13:36:01"))) %>%
  st_transform(., crs = bng_epsg)

sk2 <- read_csv("raw_data/sk2/sensors.csv", col_names = scn) %>%
  unite(., date_time, date, time, sep = " ") %>%
  mutate(., date_time = ymd_hms(date_time)) %>%
  mutate(across(scn[3:length(scn)], as.numeric))

sk2_gps <- read_csv("raw_data/sk2/adv_gps.log", col_names = gpscn) %>%
  unite(., date_time, date, time, sep = " ") %>%
  mutate(., date_time = ymd_hms(date_time)) %>%
  filter(., code == "FIX") %>%
  select(date_time, latitude, longitude)

# join data
sk2_comb_bng <- left_join(sk2_gps, sk2) %>%
  st_as_sf(., coords = c("longitude", "latitude"), crs = 4326) %>%
  filter(., !between(date_time, as_datetime("2020-07-29 09:45:03"), 
                     as_datetime("2020-07-29 10:26:59")),
         !between(date_time, as_datetime("2020-07-29 12:17:39"), 
                  as_datetime("2020-07-29 12:35:09")),
         !between(date_time, as_datetime("2020-07-29 13:55:50"),
                  as_datetime("2020-07-29 14:34:17"))) %>%
  # change data when sensors out of water to NA (only some sensors)
  mutate(across(c(2,4,22:29), ~case_when(
    between(date_time, as_datetime("2020-07-29 13:48:00"),
                                     as_datetime("2020-07-29 13:55:49")) ~ NA_real_,
            TRUE ~ .x))) %>%
  st_transform(., crs = bng_epsg)

sk3 <- read_csv("raw_data/sk3/sensors.csv", col_names = scn) %>%
  unite(., date_time, date, time, sep = " ") %>%
  mutate(., date_time = ymd_hms(date_time)) %>%
  mutate(across(scn[3:length(scn)], as.numeric))

sk3_gps <- read_csv("raw_data/sk3/adv_gps.log", col_names = gpscn) %>%
  unite(., date_time, date, time, sep = " ") %>%
  mutate(., date_time = ymd_hms(date_time)) %>%
  filter(., code == "FIX") %>%
  select(date_time, latitude, longitude)

# join data
sk3_comb_bng <- left_join(sk3_gps, sk3) %>%
  filter(., !between(date_time, as_datetime("2020-07-29 12:59:01"), 
                     as_datetime("2020-07-29 13:04:16"))) %>%
  filter(., !between(date_time, as_datetime("2020-07-29 11:08:54"),
                     as_datetime("2020-07-29 11:12:00"))) %>%
  st_as_sf(., coords = c("longitude", "latitude"), crs = 4326) %>%
  st_transform(., crs = bng_epsg)


# combine all 3 datasets
sk_all_comb_bng <- rbind(sk1_comb_bng, sk2_comb_bng, sk3_comb_bng)

#### Hex Grids ####

# manually created polygon defining a sea area of interest
harbour <- sf::st_read("raw_data/harbour_sea_poly.gpkg")
harbour_hex_grid <- st_make_grid(harbour, cellsize = hex_size, square = FALSE)
crop_hhg <- sf::st_intersection(harbour_hex_grid, harbour)

plot(harbour, col = "light blue", bg = "dark green", axes = TRUE)
plot(crop_hhg, border = "orange", add = T)

# select hexes that intersect data + add ID column for later joining
data_hhg <- crop_hhg[unique(unlist(sf::st_intersects(sk_all_comb_bng, crop_hhg)))] %>%
  sf::st_as_sf(ID = 1:length(.))

#### Making Data for Plotting ####

# temperature
mean_temp <- st_join(sk_all_comb_bng, data_hhg, join = st_intersects) %>%
  filter(., !is.na(ID)) %>%
  filter(., !is.na(temp)) %>%
  group_by(., ID) %>%
  summarise(., mean_temp = round(mean(temp),2)) %>%
  mutate(., rounded_mean_temp = plyr::round_any(mean_temp, 0.25))

mean_temp_hex <- st_join(data_hhg, mean_temp)

st_write(mean_temp_hex, "data/hex/mean_temp_hex_falmouth.gpkg", delete_dsn = TRUE)

# turbidity

# when the pm air quality sensor is measuring, then turbidity is turned off
# therefore filter values when pm is turned off (pm_running == 0)

mean_turbidity <- st_join(sk_all_comb_bng, data_hhg, join = st_intersects) %>%
  filter(., pm_running == 0) %>%
  filter(., !is.na(ID)) %>%
  filter(., !is.na(turbid_raw)) %>%
  group_by(., ID) %>%
  summarise(., mean_turbid = round(mean(turbid_raw),2)) %>%
  mutate(., mean_turbid = (mean_turbid/1024) * 3.3)
  

mean_turbid_hex <- st_join(data_hhg, mean_turbidity)

st_write(mean_turbid_hex, "data/hex/mean_turbidity_hex_falmouth.gpkg", delete_dsn = TRUE)

# pm (air quality)

# when the pm air quality sensor is measuring, then turbidity is turned off
# therefore filter values when pm is turned on (pm_running == 1)

# pm 1 std
mean_pm1_std <- st_join(sk_all_comb_bng, data_hhg, join = st_intersects) %>%
  filter(., pm_running == 1) %>%
  filter(., !is.na(ID)) %>%
  filter(., !is.na(pm_std_1_0)) %>%
  group_by(., ID) %>%
  summarise(., mean_pm = round(mean(pm_std_1_0),2))

mean_pm1_std_hex <- st_join(data_hhg, mean_pm1_std)

st_write(mean_pm1_std_hex, "data/hex/mean_pm1_std_hex_falmouth.gpkg", delete_dsn = TRUE)

# pm 2.5 std
mean_pm25_std <- st_join(sk_all_comb_bng, data_hhg, join = st_intersects) %>%
  filter(., pm_running == 1) %>%
  filter(., !is.na(ID)) %>%
  filter(., !is.na(pm_std_2_5)) %>%
  group_by(., ID) %>%
  summarise(., mean_pm = round(mean(pm_std_2_5),2))

mean_pm25_std_hex <- st_join(data_hhg, mean_pm25_std)

st_write(mean_pm25_std_hex, "data/hex/mean_pm25_std_hex_falmouth.gpkg", delete_dsn = TRUE)

# pm 10 std
mean_pm10_std <- st_join(sk_all_comb_bng, data_hhg, join = st_intersects) %>%
  filter(., pm_running == 1) %>%
  filter(., !is.na(ID)) %>%
  filter(., !is.na(pm_std_10_0)) %>%
  group_by(., ID) %>%
  summarise(., mean_pm = round(mean(pm_std_10_0),2))

mean_pm10_std_hex <- st_join(data_hhg, mean_pm10_std)

st_write(mean_pm10_std_hex, "data/hex/mean_pm10_std_hex_falmouth.gpkg", delete_dsn = TRUE)

