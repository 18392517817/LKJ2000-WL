#!/usr/bin/python
# -*-coding: utf-8 -*-

import serial
import threading
import binascii
from datetime import datetime
import struct
import csv
import time
from SNSendData import *
from SNGetData import *
from SNWLTypeDef import _SN_DataType,  _SN_VersionInfoPackage , _SN_ActiDetectionInfo,_SN_UpgradeRequestInfo ,_SN_UpgradeOperationInfo,_SN_WLActiDetectionInfo,_SN_VersionConfirmInfo,_SN_UpgradePlanCancelledReply
#10 02 18 00 01 11 10 ff 01 00 01 05 00 12 34 05 00 12 34 03 03 01 00 01 01 01 0f A8 B6 10 03
send_data =bytearray()

def SN_businesstype_handle(mSerial,datatype,data_Effbytes):
    global send_data
    if(0x1001 == datatype.PacketType):
        #活动性检测
        print("包类型：",'%#x'%datatype.PacketType)

        item = _SN_VersionInfoPackage()
        #版本信息包帧解析
        item = SN_VersionInfoPackage(data_Effbytes)
        #回复版本信息包
        send_data = SN_VersionInfoPackageReply(datatype,item)
        mSerial.send_data(send_data)

    elif(0x1002 == datatype.PacketType):
        print("包类型：",'%#x'%datatype.PacketType)
         #收到活动性检测发送，准备发送应答
        item = _SN_ActiDetectionInfo()
        #活动性检测帧解析
        item = SN_ActiDetectionInfo(data_Effbytes)
        #回复活动性检测帧
        send_data = SN_ActiDetectionInfoReply(datatype,item)
        mSerial.send_data(send_data)
    elif(0x1003 == datatype.PacketType):
        print("包类型：",'%#x'%datatype.PacketType)
         #升级信息请求
        item = _SN_UpgradeRequestInfo()

        item = SN_UpgradeRequestInfo(data_Effbytes)
        #升级信息发送
        send_data = SN_UpgradeInfoSend(datatype,item)
        mSerial.send_data(send_data)
    elif(0x1004 == datatype.PacketType):
        print("包类型：",'%#x'%datatype.PacketType)
        item = _SN_UpgradeOperationInfo()
        #升级操作信息请求
        item = SN_UpgradeOperationInfo(data_Effbytes)
        #升级操作信息应答
        send_data = SN_UpgradeOperationInfoReply(datatype,item)
        mSerial.send_data(send_data)

        #延时1秒后，发送启动升级信息
        time.sleep(0.4)
        send_data = SN_StartUpgradeOperationInfo(datatype,item)
        mSerial.send_data(send_data)

    elif(0x1005 == datatype.PacketType):
        print("包类型：",'%#x'%datatype.PacketType)
        item = _SN_StartUpgradeOperationInfoReply()
        #升级操作信息请求
        #item = SN_StartUpgradeOperationInfoReply(data_Effbytes)
    elif(0x1006 == datatype.PacketType):
        print("包类型：",'%#x'%datatype.PacketType)
         #收到活动性检测发送，准备发送应答
        item = _SN_WLActiDetectionInfo()
        #活动性检测帧解析
        item = SN_WLActiDetectionInfo(data_Effbytes)
        #回复活动性检测帧
        send_data = SN_WLActiDetectionInfoReply(datatype,item)
        mSerial.send_data(send_data)


    elif(0x1007 == datatype.PacketType):
        print("包类型：",'%#x'%datatype.PacketType)
        item = _SN_VersionConfirmInfo()
        item = SN_VersionConfirmInfo(data_Effbytes)
        send_data = SN_VersionConfirmInfoReply(datatype,item)
        mSerial.send_data(send_data)
    elif(0x1008 == datatype.PacketType):
        print("包类型：",'%#x'%datatype.PacketType)
        item = _SN_UpgradePlanCancelledReply()
        item = SN_UpgradePlanCancelledReply(data_Effbytes)
        #不回复
    else:
        print("未识别的包类型：",'%#x'%datatype.PacketType)

    return send_data


def SN_data_handle(mSerial,data_Effbytes):
    #print("有效数据处理：",str(datetime.now()),':',binascii.b2a_hex(data_Effbytes))
    data_len=len(data_Effbytes)
    i=0
    #帧格式解析
    if(data_len>=12):

        datatype = _SN_DataType()
        datatype.Resrve=struct.unpack('<H',data_Effbytes[i:i+2])[0]
        datatype.PacketType=struct.unpack('<H',data_Effbytes[i+2:i+4])[0]
        datatype.TimeStamp=struct.unpack('<I',data_Effbytes[i+4:i+8])[0]
        datatype.InfoLen=struct.unpack('<H',data_Effbytes[i+8:i+10])[0]
        datatype.PacketNum=struct.unpack('<H',data_Effbytes[i+10:i+12])[0]
        datatype.Crc = struct.unpack('<H',data_Effbytes[-2:])[0]
        #loc_str = [InfoLen,StartAddr,EndAddr,BusinessType,Order,Crc]
        #业务类型处理
        send_data = SN_businesstype_handle(mSerial,datatype,data_Effbytes)
    else:
        print("数据不正确")

    return send_data
