# Wrangle raw data from sonic kayaks and create plot ready spatial data

# strimas.com/post/hexagonal-grids/

# James P. Duffy - 2020
# james.philip.duffy@gmail.com

#### Setup ####

# ignore erroneous dates in data - they are all relative. 

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

# read in and format sensor and GNSS Data from 1 kayak

# Need to join the sound data before filtering data for start and finish as 
# the sound data is represented as "seconds from start"

# read multiple sound csvs and combine into single data frame
# data files provided by Jo Garrett
p_sound <- list.files("raw_data/hydrophone", full.names = TRUE) %>% 
  map_df(~read_csv(.)) %>%
  rename(time_from_start = time_from_start_s) %>%
  select(-X1) %>%
  arrange(time_from_start)
  
# read and format sensor data
sk1 <- read_csv("raw_data/sensors.csv", col_names = scn) %>%
  unite(., date_time, date, time, sep = " ") %>%
  mutate(., date_time = ymd_hms(date_time)) %>%
  mutate(across(scn[3:length(scn)], as.numeric))

# read and format gps data
sk1_gps <- read_csv("raw_data/adv_gps.log", col_names = gpscn) %>%
  unite(., date_time, date, time, sep = " ") %>%
  mutate(., date_time = ymd_hms(date_time)) %>%
  filter(., code == "FIX") %>%
  select(date_time, latitude, longitude)

# use the first time from sensors csv to work out true times in sound data
p_sound_sub <- p_sound %>%
  mutate(date_time = ymd_hms(sk1$date_time[1]) + time_from_start) %>%
  select(date_time, p_rms, tol_cf_125Hz, small_boats, big_boats, large_ships)

# join data - filter out start & ends out of the water
sk1_comb_bng <- left_join(sk1_gps, sk1) %>%
  left_join(., p_sound_sub) %>%
  st_as_sf(., coords = c("longitude", "latitude"), crs = 4326) %>%
  filter(., between(date_time, as_datetime("2011-11-18 08:04:57"), 
                     as_datetime("2011-11-18 09:34:34"))) %>%
  st_transform(., crs = bng_epsg)

#### Hex Grids ####

# manually created polygon defining a sea area of interest
helford <- st_read("raw_data/helford_sea_poly.gpkg")
helford_hex_grid <- st_make_grid(helford, cellsize = hex_size, square = FALSE)
crop_hhg <- sf::st_intersection(helford_hex_grid, helford)

st_write(crop_hhg, "data/hex/helford_hex_grid.gpkg", delete_dsn = TRUE)

plot(helford, col = "light blue", bg = "dark green", axes = TRUE)
plot(crop_hhg, border = "orange", add = T)

# select hexes that intersect data + add ID column for later joining
data_hhg <- crop_hhg[unique(unlist(sf::st_intersects(sk1_comb_bng, crop_hhg)))] %>%
  sf::st_as_sf(ID = 1:length(.))

#### Making Data for Plotting ####

# temperature
mean_temp <- st_join(sk1_comb_bng, data_hhg, join = st_intersects) %>%
  filter(., !is.na(ID)) %>%
  filter(., !is.na(temp)) %>%
  group_by(., ID) %>%
  summarise(., mean_temp = round(mean(temp),2)) %>%
  mutate(., rounded_mean_temp = plyr::round_any(mean_temp, 0.25))

mean_temp_hex <- st_join(data_hhg, mean_temp)

st_write(mean_temp_hex, "data/hex/mean_temp_hex_helford.gpkg", 
         delete_dsn = TRUE)

# turbidity

# when the pm air quality sensor is measuring, then turbidity is turned off
# therefore filter values when pm is turned off (pm_running == 0)

mean_turbidity <- st_join(sk1_comb_bng, data_hhg, join = st_intersects) %>%
  filter(., pm_running == 0) %>%
  filter(., !is.na(ID)) %>%
  filter(., !is.na(turbid_raw)) %>%
  group_by(., ID) %>%
  summarise(., mean_turbid = round(mean(turbid_raw),2)) %>%
  mutate(., mean_turbid = (mean_turbid/1024) * 3.3)

mean_turbid_hex <- st_join(data_hhg, mean_turbidity)

st_write(mean_turbid_hex, "data/hex/mean_turbidity_hex_helford.gpkg", 
         delete_dsn = TRUE)


# pm (air quality)

# when the pm air quality sensor is measuring, then turbidity is turned off
# therefore filter values when pm is turned on (pm_running == 1)
  
# pm 1 std
mean_pm1_std <- st_join(sk1_comb_bng, data_hhg, join = st_intersects) %>%
  filter(., pm_running == 1) %>%
  filter(., !is.na(ID)) %>%
  filter(., !is.na(pm_std_1_0)) %>%
  group_by(., ID) %>%
  summarise(., mean_pm = round(mean(pm_std_1_0),2))

mean_pm1_std_hex <- st_join(data_hhg, mean_pm1_std)

st_write(mean_pm1_std_hex, "data/hex/mean_pm1_std_hex_helford.gpkg", 
         delete_dsn = TRUE)

# pm 2.5 std
mean_pm25_std <- st_join(sk1_comb_bng, data_hhg, join = st_intersects) %>%
  filter(., pm_running == 1) %>%
  filter(., !is.na(ID)) %>%
  filter(., !is.na(pm_std_2_5)) %>%
  group_by(., ID) %>%
  summarise(., mean_pm = round(mean(pm_std_2_5),2))

mean_pm25_std_hex <- st_join(data_hhg, mean_pm25_std)

st_write(mean_pm25_std_hex, "data/hex/mean_pm25_std_hex_helford.gpkg", 
         delete_dsn = TRUE)

# pm 10 std
mean_pm10_std <- st_join(sk1_comb_bng, data_hhg, join = st_intersects) %>%
  filter(., pm_running == 1) %>%
  filter(., !is.na(ID)) %>%
  filter(., !is.na(pm_std_10_0)) %>%
  group_by(., ID) %>%
  summarise(., mean_pm = round(mean(pm_std_10_0),2))

mean_pm10_std_hex <- st_join(data_hhg, mean_pm10_std)

st_write(mean_pm10_std_hex, "data/hex/mean_pm10_std_hex_helford.gpkg", 
         delete_dsn = TRUE)


# p_rms (sound data)

mean_p_rms <- st_join(sk1_comb_bng, data_hhg, join = st_intersects) %>%
  filter(., !is.na(ID)) %>%
  filter(., !is.na(p_rms)) %>%
  group_by(., ID) %>%
  summarise(., mean_p_rms = mean(p_rms)) %>%
  mutate(mean_p_rms_db = 10*log10(mean_p_rms))

mean_p_rms_std_hex <- st_join(data_hhg, mean_p_rms)

st_write(mean_p_rms_std_hex, "data/hex/mean_p_rms_std_hex_helford.gpkg", 
         delete_dsn = TRUE)

# tol_cf_125Hz

mean_tol_cf_125hz <- st_join(sk1_comb_bng, data_hhg, join = st_intersects) %>%
  filter(., !is.na(ID)) %>%
  filter(., !is.na(tol_cf_125Hz)) %>%
  group_by(., ID) %>%
  summarise(., mean_tol_cf_125Hz = mean(tol_cf_125Hz)) %>%
  mutate(mean_tol_cf_125Hz = 10*log10(mean_tol_cf_125Hz))

mean_tol_cf_125hz_hex <- st_join(data_hhg, mean_tol_cf_125hz)

st_write(mean_tol_cf_125hz_hex, "data/hex/mean_tol_cf_125hz_std_hex_helford.gpkg", 
         delete_dsn = TRUE)


# small boats

mean_small_boats <- st_join(sk1_comb_bng, data_hhg, join = st_intersects) %>%
  filter(., !is.na(ID)) %>%
  filter(., !is.na(small_boats)) %>%
  group_by(., ID) %>%
  summarise(., mean_small_boats = mean(small_boats)) %>%
  mutate(mean_small_boats = 10*log10(mean_small_boats))

mean_small_boats_hex <- st_join(data_hhg, mean_small_boats)

st_write(mean_small_boats_hex, "data/hex/mean_small_boats_hex_helford.gpkg", 
         delete_dsn = TRUE)

# big boats

mean_big_boats <- st_join(sk1_comb_bng, data_hhg, join = st_intersects) %>%
  filter(., !is.na(ID)) %>%
  filter(., !is.na(big_boats)) %>%
  group_by(., ID) %>%
  summarise(., mean_big_boats = mean(big_boats)) %>%
  mutate(mean_big_boats = 10*log10(mean_big_boats))

mean_big_boats_hex <- st_join(data_hhg, mean_big_boats)

st_write(mean_big_boats_hex, "data/hex/mean_big_boats_hex_helford.gpkg", 
         delete_dsn = TRUE)

# large ships

mean_large_ships <- st_join(sk1_comb_bng, data_hhg, join = st_intersects) %>%
  filter(., !is.na(ID)) %>%
  filter(., !is.na(large_ships)) %>%
  group_by(., ID) %>%
  summarise(., mean_large_ships = mean(large_ships)) %>%
  mutate(mean_large_ships = 10*log10(mean_large_ships))

mean_large_ships_hex <- st_join(data_hhg, mean_large_ships)

st_write(mean_large_ships_hex, "data/hex/mean_large_ships_hex_helford.gpkg", 
         delete_dsn = TRUE)
