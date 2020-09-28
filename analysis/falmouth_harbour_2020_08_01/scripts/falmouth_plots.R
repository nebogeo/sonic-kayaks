# Plotting Falmouth Data

# James P. Duffy - 2020
# james.philip.duffy@gmail.com

#### Setup ####

library(sf)
library(ggplot2)
library(raster)
library(RStoolbox)
library(cowplot)

# note: basemap licence means it cannot be shared 
basemap <- stack("data/aerial/falmouth_harbour_merged.tif")
all_hexs <- st_read("data/hex/falmouth_hex_grid.gpkg")

hex_mean_temp <- st_read("data/hex/mean_temp_hex_falmouth.gpkg")

hex_mean_turbid <- st_read("data/hex/mean_turbidity_hex_falmouth.gpkg")

hex_mean_pm1 <- st_read("data/hex/mean_pm1_std_hex_falmouth.gpkg")
hex_mean_pm25 <- st_read("data/hex/mean_pm25_std_hex_falmouth.gpkg")
hex_mean_pm10 <- st_read("data/hex/mean_pm10_std_hex_falmouth.gpkg")

# crop basemap + hexs to slightly bigger extent of hexagons
basemap_crop <- crop(basemap, extent(hex_mean_temp) + 300)
all_hexs_crop <- st_crop(all_hexs, extent(hex_mean_temp) + 300)

#### Temperature Plots ####

# mean temperature plain
p1 <- ggRGB(img = basemap_crop, r = 1, g = 2, b = 3) +
  geom_sf(data = hex_mean_temp, alpha = 0.9, colour = "NA",
          mapping = aes(fill = rounded_mean_temp), show.legend = "polygon") +
  geom_sf(data = hex_mean_pm1, fill = "NA", alpha = 0.6, colour = "black") +
  scale_fill_viridis_c(na.value = "NA", limits = c(15.5,18),
                       breaks = c(15.5, 16, 16.5, 17, 17.5, 18)) +
  coord_sf(crs = st_crs(27700), datum = st_crs(27700), expand = 0) +
  xlab("Easting (m)") + 
  ylab("Northing (m)") +
  labs(fill = "Mean \nTemperature (ºC)") +
  guides(fill = guide_colourbar(barwidth = 2.5, barheight = 20)) +
  theme_cowplot(font_size = 20) +
  theme(legend.title.align=0.5) +
  annotate(geom="text", x = extent(basemap_crop)[1] + 300, 
           y = extent(basemap_crop)[3] + 30, 
           label="© Getmapping Plc",
           colour= "white", size = 4)

ggsave("plots/falmouth_hex_mean_temp.png", plot = p1, width = 600, 
       height = 356, dpi = 900, units = "mm")


#### Turbidity Plots ####

# mean turbidity plain
p2 <- ggRGB(img = basemap_crop, r = 1, g = 2, b = 3) +
  geom_sf(data = hex_mean_turbid, alpha = 0.9, colour = "NA",
          mapping = aes(fill = mean_turbid), show.legend = "polygon") +
  geom_sf(data = hex_mean_turbid, fill = "NA", alpha = 0.6, colour = "black") +
  scale_fill_viridis_c(na.value = "NA", limits = c(1.45, 2),
                       breaks = c(1.45, 1.50, 1.55, 1.60, 1.65, 1.70, 1.75, 1.80, 1.85, 1.90, 1.95, 2)) +
  coord_sf(crs = st_crs(27700), datum = st_crs(27700), expand = 0) +
  xlab("Easting (m)") + 
  ylab("Northing (m)") +
  labs(fill = "Mean \nTurbidity (Volts)") +
  guides(fill = guide_colourbar(barwidth = 2.5, barheight = 20)) +
  theme_cowplot(font_size = 20) +
  theme(legend.title.align=0.5) +
  annotate(geom="text", x = extent(basemap_crop)[1] + 300, 
           y = extent(basemap_crop)[3] + 30, 
           label="© Getmapping Plc",
           colour= "white", size = 4)

ggsave("plots/falmouth_hex_mean_turbid.png", plot = p2, width = 600, 
       height = 356, dpi = 900, units = "mm")


#### Air Quality Plots ####

# 0.1 
p3 <- ggRGB(img = basemap_crop, r = 1, g = 2, b = 3) +
  geom_sf(data = hex_mean_pm1, alpha = 0.9, colour = "NA",
          mapping = aes(fill = mean_pm), show.legend = "polygon") +
  geom_sf(data = hex_mean_pm1, fill = "NA", alpha = 0.6, colour = "black") +
  scale_fill_viridis_c(na.value = "NA", limits = c(0,5),
                       breaks = c(0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5)) +
  coord_sf(crs = st_crs(27700), datum = st_crs(27700), expand = 0) +
  xlab("Easting (m)") + 
  ylab("Northing (m)") +
  labs(fill = paste0("Mean \nParticulate \nMatter (µg/m3)")) +
  guides(fill = guide_colourbar(barwidth = 2.5, barheight = 20)) +
  theme_cowplot(font_size = 20) +
  theme(legend.title.align=0.5) +
  annotate(geom="text", x = extent(basemap_crop)[1] + 300, 
           y = extent(basemap_crop)[3] + 30, 
           label="© Getmapping Plc",
           colour= "white", size = 4)

ggsave("plots/falmouth_hex_mean_pm1.png", plot = p3, width = 600, 
       height = 356, dpi = 600, units = "mm")

# 2.5
p4 <- ggRGB(img = basemap_crop, r = 1, g = 2, b = 3) +
  geom_sf(data = hex_mean_pm25, alpha = 0.9, colour = "NA",
          mapping = aes(fill = mean_pm), show.legend = "polygon") +
  geom_sf(data = hex_mean_pm25, fill = "NA", alpha = 0.6, colour = "black") +
  scale_fill_viridis_c(na.value = "NA", limits = c(0,5.5),
                       breaks = c(0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5)) +
  coord_sf(crs = st_crs(27700), datum = st_crs(27700), expand = 0) +
  xlab("Easting (m)") + 
  ylab("Northing (m)") +
  labs(fill = paste0("Mean \nParticulate \nMatter (µg/m3)")) +
  guides(fill = guide_colourbar(barwidth = 2.5, barheight = 20)) +
  theme_cowplot(font_size = 20) +
  theme(legend.title.align=0.5) +
  annotate(geom="text", x = extent(basemap_crop)[1] + 300, 
           y = extent(basemap_crop)[3] + 30, 
           label="© Getmapping Plc",
           colour= "white", size = 4)

ggsave("plots/falmouth_hex_mean_pm25.png", plot = p4, width = 600, 
       height = 356, dpi = 600, units = "mm")


# 10
p5 <- ggRGB(img = basemap_crop, r = 1, g = 2, b = 3) +
  geom_sf(data = hex_mean_pm10, alpha = 0.9, colour = "NA",
          mapping = aes(fill = mean_pm), show.legend = "polygon") +
  geom_sf(data = hex_mean_pm10, fill = "NA", alpha = 0.6, colour = "black") +
  scale_fill_viridis_c(na.value = "NA", limits = c(0,9),
                       breaks = c(0,1,2,3,4,5,6,7,8,9)) +
  coord_sf(crs = st_crs(27700), datum = st_crs(27700), expand = 0) +
  xlab("Easting (m)") + 
  ylab("Northing (m)") +
  labs(fill = paste0("Mean \nParticulate \nMatter (µg/m3)")) +
  guides(fill = guide_colourbar(barwidth = 2.5, barheight = 20)) +
  theme_cowplot(font_size = 20) +
  theme(legend.title.align=0.5) +
  annotate(geom="text", x = extent(basemap_crop)[1] + 300, 
           y = extent(basemap_crop)[3] + 30, 
           label="© Getmapping Plc",
           colour= "white", size = 4)

ggsave("plots/falmouth_hex_mean_pm10.png", plot = p5, width = 600, 
       height = 356, dpi = 600, units = "mm")
