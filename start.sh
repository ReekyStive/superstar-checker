#!/bin/bash
check_sys(){
	if [[ -f /etc/redhat-release ]]; then
		release="centos"
	elif cat /etc/issue | grep -q -E -i "debian"; then
		release="debian"
	elif cat /etc/issue | grep -q -E -i "ubuntu"; then
		release="ubuntu"
	elif cat /etc/issue | grep -q -E -i "centos|red hat|redhat"; then
		release="centos"
	elif cat /proc/version | grep -q -E -i "debian"; then
		release="debian"
	elif cat /proc/version | grep -q -E -i "ubuntu"; then
		release="ubuntu"
	elif cat /proc/version | grep -q -E -i "centos|red hat|redhat"; then
		release="centos"
    fi
	bit=`uname -m`
}

#安装python3
Installation_dependency(){
	if [[ ${release} = "centos" ]]; then
		yum update
    yum install screen
		wget https://www.moerats.com/usr/shell/Python3/CentOS_Python3.6.sh && sh CentOS_Python3.6.sh
	if [[ ${release} = "debian" ]]; then
	  apt update
    apt-get install screen
		wget https://www.moerats.com/usr/shell/Python3/Debian_Python3.6.sh && sh Debian_Python3.6.sh
  if [[ ${release} = "ubuntu" ]]; then    
    apt update
    apt-get install screen
    apt install python3-pip python3-setuptools python3-dev python3-wheel build-essential -y
	fi
}
screen -S fastapi
cd /chaoxing_auto_sign/api
pip3 install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 9090
