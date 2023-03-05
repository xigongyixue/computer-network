#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import socket
import os
import sys
import struct
import time
import select
import binascii  


ICMP_ECHO_REQUEST = 8 #ICMP type code for echo request messages
ICMP_ECHO_REPLY = 0 #ICMP type code for echo reply messages


def checksum(string): 
	csum = 0
	countTo = (len(string) // 2) * 2  
	count = 0

	while count < countTo:
		thisVal = string[count+1] * 256 + string[count]
		csum = csum + thisVal 
		csum = csum & 0xffffffff  
		count = count + 2
	
	if countTo < len(string):
		csum = csum + string[len(string) - 1]
		csum = csum & 0xffffffff 
	
	csum = (csum >> 16) + (csum & 0xffff)
	csum = csum + (csum >> 16)
	answer = ~csum 
	answer = answer & 0xffff 
	answer = answer >> 8 | (answer << 8 & 0xff00)

	answer = socket.htons(answer)

	return answer
	
def receiveOnePing(icmpSocket, destinationAddress, ID, timeout):
	recv_packet, addr = icmpSocket.recvfrom(1024)
	type, code, checksum, packet_ID, sequence = struct.unpack("bbHHh", recv_packet[20:28]) 
	return time.time()-timeout
	# 1. Wait for the socket to receive a reply
	# 2. Once received, record time of receipt, otherwise, handle a timeout
	# 3. Compare the time of receipt to time of sending, producing the total network delay
	# 4. Unpack the packet header for useful information, including the ID
	# 5. Check that the ID matches between the request and reply
	# 6. Return total network delay
	
def sendOnePing(icmpSocket, destinationAddress, ID):
	header = struct.pack('bbHHh', 8, 0, 0, 12345, 0)  # 创建头部
	data = struct.pack('d', time.time())  # 创建data数据 时间戳随机
	packet = header + data
	chkSum = checksum(packet)
	header = struct.pack('bbHHh', 8, 0, chkSum, 12345, 0)
	icmp_data = header + data
	icmpSocket.sendto(icmp_data,(destinationAddress,ID))
	return time.time()
	# 1. Build ICMP header
	# 2. Checksum ICMP packet using given function
	# 3. Insert checksum into packet
	# 4. Send packet using socket
	# 5. Record time of sending
	
def doOnePing(destinationAddress, timeout): 
	s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
    s.connect((destinationAddress, 5000))
    sendOnePing(s,destinationAddress,5000)
    delay = receiveOnePing(s,destinationAddress,5000,timeout)
    s.close()
    return delay
	# 1. Create ICMP socket
	# 2. Call sendOnePing function
	# 3. Call receiveOnePing function
	# 4. Close ICMP socket
	# 5. Return total network delay
	
def ping(host, timeout=1):
	ip = socket.gethostbyname(host)
	while 1:
		print(doOnePing(ip,time.time()))
		time.sleep(1)
	# 1. Look up hostname, resolving it to an IP address
	# 2. Call doOnePing function, approximately every second
	# 3. Print out the returned delay
	# 4. Continue this process until stopped	

ping("lancaster.ac.uk")

# ICMP，全称是 Internet Control Message Protocol
# ping 主要是用来查看到目的地址的时延和丢包情况，
# tracert是用来查看所经过的每一跳路由，可以具体判断时延变大或者丢包的点
# Tracert命令用来显示数据包到达目标主机所经过的路径（路由器 并显示到达每个节点（路由器）的时间

# RTT(Round Trip Time)：一个连接的往返时间，即数据发送时刻到接收到确认的时刻的差值
# select socket
# socket是一组编程接口(API)，也称为套接口或套接字,是一组协议无关的编程接口
# 它是计算机之间进行通信的一种约定或一种方式。通过 socket 这种约定，一台计算机可以接收其他计算机的数据，也可以向其他计算机发送数据。