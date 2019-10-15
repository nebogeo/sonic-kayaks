-- Swamp Bike Opera embedded system for Kaffe Matthews
-- Copyright (C) 2012 Wolfgang Hauptfleisch, Dave Griffiths
--
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with this program.  If not, see <http://www.gnu.org/licenses/>.

module("gps", package.seeall)

require 'posix'
require 'socket'
require 'std'
require 'utils'
require ('osc.client')

local testing=false
--local testing_pos={lat=50.16732454840163,lng=-5.098278522491455}
--local testing_pos={lat=51.475670,lng=-0.037010}
--local testing_pos={lat=41.147387819527,lng=-8.6317899816589}
--{lat=41.140157986104,lng=-8.6173141712656}
--{lat=51.04790318580878,lng=3.7287747859954834}
--{lat=51.04803133876788,lng=3.730437755584717}
-- {lat=50.1729952601643,lng=-5.106239318847656}
-- {lat=50.16647031001818,lng=-5.097473859786987}

local test_time=0

---
-- convert wgs data to location
function wgs_to_dec(lat, sign1, lon, sign2)

    --print("lat:"..lat.." sign:"..sign1.." lon:"..lon.." sign2:"..sign2)
    local d,m,r = string.match(lat, "(%d%d)(%d%d).(%d%d%d%d)")
    local s = ( 60 / 10000 ) * r
    local lat_deg = d + (m/60) + (s/3600)

    local d,m,r = string.match(lon, "(%d%d)(%d%d).(%d%d%d%d)")
    local s = ( 60 / 10000 ) * r
    local lon_deg = d + (m/60) + (s/3600)

    if sign2 == "W" then
       lon_deg = lon_deg * - 1
    end

    local file = io.open("/tmp/swamp_gps", "w")
    if testing then
        file:write(std.round(testing_pos.lat, 10).." "..
                   std.round(testing_pos.lng, 10))

	print("testing_pos:"..testing_pos.lat..", "..testing_pos.lng)
        testing_pos.lat=testing_pos.lat+0.0001*math.cos(test_time)
        testing_pos.lng=testing_pos.lng+0.0001*math.sin(test_time)

        test_time=test_time+0.1
    else
        file:write(std.round(lat_deg, 10).." "..std.round(lon_deg, 10))
    end

    file:close()
end

-- copied from https://github.com/jvermillard/lua-nmea/blob/master/src/nmea.lua
-- looks like there is no standard split string function in lua
function split(s,re)
    local i1 = 1
    local ls = {}
    local append = table.insert
    if not re then re = '%s+' end
    if re == '' then return {s} end
    while true do
        local i2,i3 = s:find(re,i1)
        if not i2 then
            local last = s:sub(i1)
            if last ~= '' then append(ls,last) end
            if #ls == 1 and ls[1] == '' then
                return {}
            else
                return ls
            end
        end
        append(ls,s:sub(i1,i2-1))
        i1 = i3+1
    end
end

--- main loop
--@param device number
function loop(device, logfile)
    local logged_nolock=false
    local logged_lock=false
    local msg
    dev = io.open(device)
    for line in dev:lines() do
        local data = split(line,",")
        if data[1] == "$GPGGA" then
            if data[3] ~= ""  and data[5] ~= "" then
                if not logged_lock then
	            utils.log(logfile, "GPS locked")
	            logged_nolock = false
	            logged_lock = true
                end
                lat = data[3]
                sign1 = data[4]
                lon = data[5]
                sign2 = data[6]
                wgs_to_dec(lat, sign1, lon, sign2)
            else
                msg = "No GPS lock"
	        --print(msg)
                if not logged_nolock then
	          utils.log(logfile, msg)
                  logged_nolock = true
                  logged_lock = false
                end 
            end
        end
    end
    return false
end

---
--@return device number or false
function detect_device()
    for i=0,20 do
       if io.open("/dev/ttyUSB"..i) then
         return i
       end
    end
    return false
end


---
function startup(dev, logfile)
    posix.mkfifo("/tmp/swamp_gps")
    while true do
        if dev then
            loop(dev, logfile)
        else
            break
        end
    end
end
