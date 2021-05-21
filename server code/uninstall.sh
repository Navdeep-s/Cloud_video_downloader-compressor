systemctl disable my_cloud  
rm /etc/systemd/system/my_cloud.service
systemctl stop my_cloud
systemctl daemon-reload
