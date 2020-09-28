# Plotting Helford data 

# James P. Duffy - 2020
# james.philip.duffy@gmail.com

#### Setup ####

library(sf)
library(ggplot2)
library(raster)
library(RStoolbox)
library(cowplot)

# note: basemap licence means it cannot be shared 
basemap <- stack("data/aerial/helford_2013_merged.tif")
all_hexs <- st_read("data/hex/helford_hex_grid.gpkg")

hex_mean_temp <- st_read("data/hex/mean_temp_hex_helford.gpkg")

hex_mean_turbid <- st_read("data/hex/mean_turbidity_hex_helford.gpkg")

hex_mean_pm1 <- st_read("data/hex/mean_pm1_std_hex_helford.gpkg")
hex_mean_pm25 <- st_read("data/hex/mean_pm25_std_hex_helford.gpkg")
hex_mean_pm10 <- st_read("data/hex/mean_pm10_std_hex_helford.gpkg")

hex_mean_p_rms <- st_read("data/hex/mean_p_rms_std_hex_helford.gpkg")
hex_mean_tol_cf_125hz <- st_read("data/hex/mean_tol_cf_125hz_std_hex_helford.gpkg")
hex_mean_small_boats <- st_read("data/hex/mean_small_boats_hex_helford.gpkg")
hex_mean_big_boats <- st_read("data/hex/mean_big_boats_hex_helford.gpkg")
hex_mean_large_ships <- st_read("data/hex/mean_large_ships_hex_helford.gpkg")


# crop basemap + hexs to slightly bigger extent of hexagons
basemap_crop <- crop(basemap, extent(hex_mean_temp) + 300)
all_hexs_crop <- st_crop(all_hexs, extent(hex_mean_temp) + 300)

#### Temperature Plots ####

# mean temperature plain
p1 <- ggRGB(img = basemap_crop, r = 1, g = 2, b = 3) +
  geom_sf(data = hex_mean_temp, alpha = 0.9, colour = "NA",
          mapping = aes(fill = rounded_mean_temp), show.legend = "polygon") +
  geom_sf(data = hex_mean_pm1, fill = "NA", alpha = 0.6, colour = "black") +
  scale_fill_viridis_c(na.value = "NA") +
  coord_sf(crs = st_crs(27700), datum = st_crs(27700), expand = 0) +
  xlab("Easting (m)") + 
  ylab("Northing (m)") +
  labs(fill = "Mean \nTemperature (ºC)") +
  guides(fill = guide_colourbar(barwidth = 2.5, barheight = 20)) +
  theme_cowplot(font_size = 20) +
  theme(legend.title.align=0.5) +
  annotate(geom="text", x = extent(basemap_crop)[1] + 90, 
           y = extent(basemap_crop)[3] + 30, 
           label="© Getmapping Plc",
           colour= "white", size = 4)

ggsave("plots/helford_hex_mean_temp.png", plot = p1, width = 400, 
       height = 356, dpi = 600, units = "mm")


#### Turbidity Plots ####

# mean turbidity plain
p2 <- ggRGB(img = basemap_crop, r = 1, g = 2, b = 3) +
  geom_sf(data = hex_mean_turbid, alpha = 0.9, colour = "NA",
          mapping = aes(fill = mean_turbid), show.legend = "polygon") +
  geom_sf(data = hex_mean_turbid, fill = "NA", alpha = 0.6, colour = "black") +
  scale_fill_viridis_c(na.value = "NA", limits = c(1.45, 1.60),
                       breaks = c(1.450, 1.475, 1.500, 1.525, 1.550, 1.575, 1.600 )) +
  coord_sf(crs = st_crs(27700), datum = st_crs(27700), expand = 0) +
  xlab("Easting (m)") + 
  ylab("Northing (m)") +
  labs(fill = "Mean \nTurbidity (Volts)") +
  guides(fill = guide_colourbar(barwidth = 2.5, barheight = 20)) +
  theme_cowplot(font_size = 20) +
  theme(legend.title.align=0.5) +
  annotate(geom="text", x = extent(basemap_crop)[1] + 90, 
           y = extent(basemap_crop)[3] + 30, 
           label="© Getmapping Plc",
           colour= "white", size = 4)


ggsave("plots/helford_hex_mean_turbid.png", plot = p2, width = 400, 
       height = 356, dpi = 600, units = "mm")


#### Air Quality Plots ####

# 0.1 
p3 <- ggRGB(img = basemap_crop, r = 1, g = 2, b = 3) +
  geom_sf(data = hex_mean_pm1, alpha = 0.9, colour = "NA",
          mapping = aes(fill = mean_pm), show.legend = "polygon") +
  geom_sf(data = hex_mean_pm1, fill = "NA", alpha = 0.6, colour = "black") +
  scale_fill_viridis_c(na.value = "NA", limits = c(2,9),
                       breaks = c(2,3,4,5,6,7,8,9)) +
  coord_sf(crs = st_crs(27700), datum = st_crs(27700), expand = 0) +
  xlab("Easting (m)") + 
  ylab("Northing (m)") +
  labs(fill = paste0("Mean \nParticulate \nMatter (µg/m3)")) +
  guides(fill = guide_colourbar(barwidth = 2.5, barheight = 20)) +
  theme_cowplot(font_size = 20) +
  theme(legend.title.align=0.5) +
  annotate(geom="text", x = extent(basemap_crop)[1] + 90, 
           y = extent(basemap_crop)[3] + 30, 
           label="© Getmapping Plc",
           colour= "white", size = 4)

ggsave("plots/helford_hex_mean_pm1.png", plot = p3, width = 400, 
       height = 356, dpi = 600, units = "mm")

#2.5
p4 <- ggRGB(img = basemap_crop, r = 1, g = 2, b = 3) +
  geom_sf(data = hex_mean_pm25, alpha = 0.9, colour = "NA",
          mapping = aes(fill = mean_pm), show.legend = "polygon") +
  geom_sf(data = hex_mean_pm1, fill = "NA", alpha = 0.6, colour = "black") +
  scale_fill_viridis_c(na.value = "NA", limits = c(3,14),
                       breaks = c(3,4,5,6,7,8,9,10,11,12,13,14)) +
  coord_sf(crs = st_crs(27700), datum = st_crs(27700), expand = 0) +
  xlab("Easting (m)") + 
  ylab("Northing (m)") +
  labs(fill = paste0("Mean \nParticulate \nMatter (µg/m3)")) +
  guides(fill = guide_colourbar(barwidth = 2.5, barheight = 20)) +
  theme_cowplot(font_size = 20) +
  theme(legend.title.align=0.5) +
  annotate(geom="text", x = extent(basemap_crop)[1] + 90, 
           y = extent(basemap_crop)[3] + 30, 
           label="© Getmapping Plc",
           colour= "white", size = 4)

ggsave("plots/helford_hex_mean_pm25.png", plot = p4, width = 400, 
       height = 356, dpi = 600, units = "mm")

#10
p5 <- ggRGB(img = basemap_crop, r = 1, g = 2, b = 3) +
  geom_sf(data = hex_mean_pm10, alpha = 0.9, colour = "NA",
          mapping = aes(fill = mean_pm), show.legend = "polygon") +
  geom_sf(data = hex_mean_pm1, fill = "NA", alpha = 0.6, colour = "black") +
  scale_fill_viridis_c(na.value = "NA", limits = c(2.5,20),
                       breaks = c(2.5,5,7.5,10,12.5,15,17.5,20)) +
  coord_sf(crs = st_crs(27700), datum = st_crs(27700), expand = 0) +
  xlab("Easting (m)") + 
  ylab("Northing (m)") +
  labs(fill = paste0("Mean \nParticulate \nMatter (µg/m3)")) +
  guides(fill = guide_colourbar(barwidth = 2.5, barheight = 20)) +
  theme_cowplot(font_size = 20) +
  theme(legend.title.align=0.5) +
  annotate(geom="text", x = extent(basemap_crop)[1] + 90, 
           y = extent(basemap_crop)[3] + 30, 
           label="© Getmapping Plc",
           colour= "white", size = 4)

ggsave("plots/helford_hex_mean_pm10.png", plot = p5, width = 400, 
       height = 356, dpi = 600, units = "mm")


#### Sound Plots ####

# p_rms

leg_title <- bquote(atop(Broadband~Mean~SPL[rms]~phantom(),
                          dB~re~1~µPa~phantom()))

p6 <- ggRGB(img = basemap_crop, r = 1, g = 2, b = 3) +
  geom_sf(data = hex_mean_p_rms, alpha = 0.9, colour = "NA",
          mapping = aes(fill = mean_p_rms_db), show.legend = "polygon") +
  geom_sf(data = hex_mean_p_rms, fill = "NA", alpha = 0.6, colour = "black") +
  scale_fill_viridis_c(na.value = "NA", limits = c(87.5,112.5),
                       breaks = c(87.5,90,92.5,95,97.5,100,102.5,105,107.5,110,112.5)) +
  coord_sf(crs = st_crs(27700), datum = st_crs(27700), expand = 0) +
  xlab("Easting (m)") + 
  ylab("Northing (m)") +
  labs(fill = leg_title) +
  guides(fill = guide_colourbar(barwidth = 2.5, barheight = 20)) +
  theme_cowplot(font_size = 20) +
  annotate(geom="text", x = extent(basemap_crop)[1] + 90, 
           y = extent(basemap_crop)[3] + 30, 
           label="© Getmapping Plc",
           colour= "white", size = 4)

ggsave("plots/helford_hex_mean_p_rms.png", plot = p6, width = 400, 
       height = 356, dpi = 600, units = "mm")


# tol_cf_125Hz

leg_title <- bquote(atop(125~Hz~Mean~TOL~phantom(),
                         dB~re~1~µPa)~phantom())

p7 <- ggRGB(img = basemap_crop, r = 1, g = 2, b = 3) +
  geom_sf(data = hex_mean_tol_cf_125hz, alpha = 0.9, colour = "NA",
          mapping = aes(fill = mean_tol_cf_125Hz), show.legend = "polygon") +
  geom_sf(data = hex_mean_tol_cf_125hz, fill = "NA", alpha = 0.6, colour = "black") +
  scale_fill_viridis_c(na.value = "NA", limits = c(60,95),
                       breaks = c(60,65,70,75,80,85,90,95)) +
  coord_sf(crs = st_crs(27700), datum = st_crs(27700), expand = 0) +
  xlab("Easting (m)") + 
  ylab("Northing (m)") +
  labs(fill = leg_title) +
  guides(fill = guide_colourbar(barwidth = 2.5, barheight = 20)) +
  theme_cowplot(font_size = 20) +
  annotate(geom="text", x = extent(basemap_crop)[1] + 90, 
           y = extent(basemap_crop)[3] + 30, 
           label="© Getmapping Plc",
           colour= "white", size = 4)

ggsave("plots/helford_hex_mean_tol_cf_125hz.png", plot = p7, width = 400, 
       height = 356, dpi = 600, units = "mm")


# small boats

leg_title <- bquote(atop(Small~Boats~Mean~SPL[rms]~phantom(),
                         dB~re~1~µPa~phantom()))

p8 <- ggRGB(img = basemap_crop, r = 1, g = 2, b = 3) +
  geom_sf(data = hex_mean_small_boats, alpha = 0.9, colour = "NA",
          mapping = aes(fill = mean_small_boats), show.legend = "polygon") +
  geom_sf(data = hex_mean_small_boats, fill = "NA", alpha = 0.6, colour = "black") +
  scale_fill_viridis_c(na.value = "NA", limits =c(75,110),
                       breaks = c(75,80,85,90,95,100,105,110)) +
  coord_sf(crs = st_crs(27700), datum = st_crs(27700), expand = 0) +
  xlab("Easting (m)") + 
  ylab("Northing (m)") +
  labs(fill = leg_title) +
  guides(fill = guide_colourbar(barwidth = 2.5, barheight = 20)) +
  theme_cowplot(font_size = 20) +
  annotate(geom="text", x = extent(basemap_crop)[1] + 90, 
           y = extent(basemap_crop)[3] + 30, 
           label="© Getmapping Plc",
           colour= "white", size = 4)

ggsave("plots/helford_hex_mean_small_boats.png", plot = p8, width = 400, 
       height = 356, dpi = 600, units = "mm")


# big boats

leg_title <- bquote(atop(Big~Boats~Mean~SPL[rms]~phantom(),
                         dB~re~1~µPa~phantom()))

p9 <- ggRGB(img = basemap_crop, r = 1, g = 2, b = 3) +
  geom_sf(data = hex_mean_big_boats, alpha = 0.9, colour = "NA",
          mapping = aes(fill = mean_big_boats), show.legend = "polygon") +
  geom_sf(data = hex_mean_big_boats, fill = "NA", alpha = 0.6, colour = "black") +
  scale_fill_viridis_c(na.value = "NA", limits = c(75,110),
                       breaks = c(75,80,85,90,95,100,105,110)) +
  coord_sf(crs = st_crs(27700), datum = st_crs(27700), expand = 0) +
  xlab("Easting (m)") + 
  ylab("Northing (m)") +
  labs(fill = leg_title) +
  guides(fill = guide_colourbar(barwidth = 2.5, barheight = 20)) +
  theme_cowplot(font_size = 20) +
  annotate(geom="text", x = extent(basemap_crop)[1] + 90, 
           y = extent(basemap_crop)[3] + 30, 
           label="© Getmapping Plc",
           colour= "white", size = 4)

ggsave("plots/helford_hex_mean_big_boats.png", plot = p9, width = 400, 
       height = 356, dpi = 600, units = "mm")


# large ships

leg_title <- bquote(atop(Large~Ships~Mean~SPL[rms]~phantom(),
                         dB~re~1~µPa~phantom()))

p10 <- ggRGB(img = basemap_crop, r = 1, g = 2, b = 3) +
  geom_sf(data = hex_mean_large_ships, alpha = 0.9, colour = "NA",
          mapping = aes(fill = mean_large_ships), show.legend = "polygon") +
  geom_sf(data = hex_mean_large_ships, fill = "NA", alpha = 0.6, colour = "black") +
  scale_fill_viridis_c(na.value = "NA", limits = c(85, 105),
                       breaks = c(85,90,95,100,105)) +
  coord_sf(crs = st_crs(27700), datum = st_crs(27700), expand = 0) +
  xlab("Easting (m)") + 
  ylab("Northing (m)") +
  labs(fill = leg_title) +
  guides(fill = guide_colourbar(barwidth = 2.5, barheight = 20)) +
  theme_cowplot(font_size = 20) +
  annotate(geom="text", x = extent(basemap_crop)[1] + 90, 
           y = extent(basemap_crop)[3] + 30, 
           label="© Getmapping Plc",
           colour= "white", size = 4)

ggsave("plots/helford_hex_mean_large_ships.png", plot = p10, width = 400, 
       height = 356, dpi = 600, units = "mm")
