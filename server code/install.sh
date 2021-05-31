apt-get update
apt-get install aria2
apt-get install ffmpeg
apt-get install python3-pip
pip3 install opencv-python


file="test.txt"

script_file="start_script.sh"
echo "#!/bin/sh" >> $script_file
echo "cd \"$(pwd)\"" >> $script_file
echo "python3 server.py" >> $script_file

chmod +x $script_file




echo "[Unit]" > $file
echo "Description=My server" >> $file
echo  >> $file
echo "[Service]" >> $file
echo ExecStart="\"$(pwd)/$script_file\"" >> $file
echo  >> $file
echo "[Install]" >> $file
echo "WantedBy=multi-user.target" >> $file

echo "enter ip address of your machine"
read ip_addr
echo "enter the port on which you want to host the service"
read port
echo "{ \"ip\" : \"$ip_addr\",\"port\" :  $port }" > config.json
mv $file /etc/systemd/system/my_cloud.service
systemctl enable my_cloud  
systemctl daemon-reload
systemctl restart my_cloud
