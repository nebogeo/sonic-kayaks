killall jackd
killall pd

# make sure we are connected...
echo 'power off' | bluetoothctl
sleep 1
echo 'power on' | bluetoothctl
sleep 5
echo 'connect C0:28:8D:F7:56:CA' | bluetoothctl
sleep 5
# test the speaker
aplay -D bluetooth ~/startup.wav
# start the jack server now
jackd -dalsa -dbluetooth -p2048 -r44100 > /home/pi/stick/sonickayak/logs/jackd.log 2>&1   &
sleep 3
# connect to the usb sound card as an input
alsa_in -d hw:1 &
# (running this the other way around - server on usb,
# with bluetooth as jack_out seems to cause a segfault)

# start pd
pd -nogui -jack -path /home/pi/pd-iemnet:/home/pi/osc /home/pi/stick/sonickayak/pd/sonickayak.pd > /home/pi/stick/sonickayak/logs/puredate.log 2>&1  &    

#sleep 10
# cpnnect pd to the usb input
#jack_connect alsa_in:capture_1 pure_data_0:input0




