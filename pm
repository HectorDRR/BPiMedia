cd ~/minidlna-1.1.4
make
sudo service minidlna stop
sleep 2
sudo cp minidlnad /usr/local/sbin/
sudo service minidlna start
sleep 2
tail /var/log/minidlna.log

