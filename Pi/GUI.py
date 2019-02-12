#!/usr/bin/python
from datetime import datetime #used for time conversions and logging timestamps
import os #used to remove database on program exit
os.environ['KIVY_GL_BACKEND'] = 'gl' #need this to fix a kivy segfault that occurs with python3 for some reason
import subprocess #used to start/stop Javascript telemetry program
import sqlite3 #javascript stores telemetry in sqlite db
import time #used for time
import math #used for math
import serial #used to send data over serial to arduino
import ephem #used for TLE orbit information on orbit screen
import pytz #used for timezone conversion in orbit pass predictions
from bs4 import BeautifulSoup #used to parse webpages for data (EVA stats, ISS TLE)
import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.network.urlrequest import UrlRequest #using this to request webpages
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition

# Create Program Logs
mimiclog = open('/home/pi/Mimic/Pi/Logs/mimiclog.txt', 'w')
sgantlog = open('/home/pi/Mimic/Pi/Logs/sgantlog.txt', 'a+')
locationlog = open('/home/pi/Mimic/Pi/Logs/locationlog.txt', 'a')
testlog = open('/home/pi/Mimic/Pi/Logs/testlog.txt', 'w')
testlog.write('test')

def logWrite(string):
    mimiclog.write(str(datetime.utcnow()))
    mimiclog.write(' ')
    mimiclog.write(str(string))
    mimiclog.write('\n')

mimiclog.write("test")
logWrite("Initialized Mimic Program Log")

#-------------------------Look for a connected arduino-----------------------------------
SerialConnection1 = False
SerialConnection2 = False
SerialConnection3 = False
SerialConnection4 = False
SerialConnection5 = False

try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0)
except Exception:
    logWrite("Warning - Serial Connection ACM0 not found")
    SerialConnection1 = False
    ser = None
else:
    SerialConnection1 = True
    logWrite("Successful connection to Serial on ACMO")
    print(str(ser))

try:
    ser2 = serial.Serial('/dev/ttyACM1', 9600, timeout=0)
except Exception:
    #logWrite("Warning - Serial Connection ACM1 not found")
    SerialConnection2 = False
    ser2 = None
else:
    SerialConnection2 = True
    logWrite("Successful connection to Serial on ACM1")
    print(str(ser2))

try:
    ser3 = serial.Serial('/dev/ttyACM2', 9600, timeout=0)
except Exception:
    #logWrite("Warning - Serial Connection ACM2 not found")
    SerialConnection3 = False
    ser3 = None
else:
    SerialConnection3 = True
    logWrite("Successful connection to Serial on ACM2")
    print(str(ser3))

try:
    ser4 = serial.Serial('/dev/ttyAMA00', 9600, timeout=0)
except Exception:
    #logWrite("Warning - Serial Connection AMA00 not found")
    SerialConnection4 = False
    ser4 = None
else:
    SerialConnection4 = True
    logWrite("Successful connection to Serial on AMA0O")
    print(str(ser4))

try:
    ser5 = serial.Serial('/dev/ttyUSB0', 9600, timeout=0)
except Exception:
    #logWrite("Warning - Serial Connection USB0 not found")
    SerialConnection5 = False
    ser5 = None
else:
    SerialConnection5 = True
    logWrite("Successful connection to Serial on USBO")
    print(str(ser5))

#----------------Open SQLITE3 Database that holds the current ISS Telemetry--------------
conn = sqlite3.connect('/dev/shm/iss_telemetry.db')
conn.isolation_level = None
c = conn.cursor()
#now we populate the blank database, this prevents locked database issues
c.execute("pragma journal_mode=wal");
c.execute("CREATE TABLE IF NOT EXISTS telemetry (`Label` TEXT PRIMARY KEY, `Timestamp` TEXT, `Value` TEXT, `ID` TEXT, `dbID` NUMERIC )");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('psarj', '0', '0', 'S0000004', 0)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('ssarj', '0', '0', 'S0000003', 1)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('ptrrj', '0', '0', 'S0000002', 2)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('strrj', '0', '0', 'S0000001', 3)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('beta1b', '0', '0', 'S6000008', 4)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('beta1a', '0', '0', 'S4000007', 5)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('beta2b', '0', '0', 'P6000008', 6)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('beta2a', '0', '0', 'P4000007', 7)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('beta3b', '0', '0', 'S6000007', 8)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('beta3a', '0', '0', 'S4000008', 9)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('beta4b', '0', '0', 'P6000007', 10)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('beta4a', '0', '0', 'P4000008', 11)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('aos', '0', '0', 'AOS', 12)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('los', '0', '0', 'LOS', 13)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('sasa1_elevation', '0', '0', 'S1000005', 14)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('sgant_elevation', '0', '0', 'Z1000014', 15)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('crewlock_pres', '0', '0', 'AIRLOCK000049', 16)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('sgant_xel', '0', '0', 'Z1000015', 17)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('sasa1_azimuth', '0', '0', 'S1000004', 18)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('loopb_flowrate', '0', '0', 'P1000001', 19)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('loopb_pressure', '0', '0', 'P1000002', 20)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('loopb_temp', '0', '0', 'P1000003', 21)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('loopa_flowrate', '0', '0', 'S1000001', 22)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('loopa_pressure', '0', '0', 'S1000002', 23)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('loopa_temp', '0', '0', 'S1000003', 24)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('voltage_1a', '0', '0', 'S4000001', 25)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('voltage_1b', '0', '0', 'S6000004', 26)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('voltage_2a', '0', '0', 'P4000001', 27)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('voltage_2b', '0', '0', 'P6000004', 28)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('voltage_3a', '0', '0', 'S4000004', 29)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('voltage_3b', '0', '0', 'S6000001', 30)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('voltage_4a', '0', '0', 'P4000004', 31)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('voltage_4b', '0', '0', 'P6000001', 32)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('current_1a', '0', '0', 'S4000002', 33)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('current_1b', '0', '0', 'S6000005', 34)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('current_2a', '0', '0', 'P4000002', 35)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('current_2b', '0', '0', 'P6000005', 36)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('current_3a', '0', '0', 'S4000005', 37)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('current_3b', '0', '0', 'S6000002', 38)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('current_4a', '0', '0', 'P4000005', 39)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('current_4b', '0', '0', 'P6000002', 40)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('kuband_transmit', '0', '0', 'Z1000013', 41)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('ptrrj_mode', '0', '0', 'S0000006', 42)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('strrj_mode', '0', '0', 'S0000007', 43)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('psarj_mode', '0', '0', 'S0000008', 44)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('ssarj_mode', '0', '0', 'S0000009', 45)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('russian_mode', '0', '0', 'RUSSEG000001', 46)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('iss_mode', '0', '0', 'USLAB000086', 47)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('iss_mass', '0', '0', 'USLAB000039', 48)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('us_gnc_mode', '0', '0', 'USLAB000012', 49)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('sasa2_elevation', '0', '0', 'P1000005', 50)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('sasa2_azimuth', '0', '0', 'P1000004', 51)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('sasa2_status', '0', '0', 'P1000007', 52)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('sasa1_status', '0', '0', 'S1000009', 53)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('active_sasa', '0', '0', 'USLAB000092', 54)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('position_x', '0', '0', 'USLAB000032', 55)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('position_y', '0', '0', 'USLAB000033', 56)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('position_z', '0', '0', 'USLAB000034', 57)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('velocity_x', '0', '0', 'USLAB000035', 58)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('velocity_y', '0', '0', 'USLAB000036', 59)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('velocity_z', '0', '0', 'USLAB000037', 60)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('PSA_EMU1_VOLTS', '0', '0', 'AIRLOCK000001', 61)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('PSA_EMU1_AMPS', '0', '0', 'AIRLOCK000002', 62)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('PSA_EMU2_VOLTS', '0', '0', 'AIRLOCK000003', 63)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('PSA_EMU2_AMPS', '0', '0', 'AIRLOCK000004', 64)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('PSA_IRU_Utility_VOLTS', '0', '0', 'AIRLOCK000005', 65)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('PSA_IRU_Utility_AMPS', '0', '0', 'AIRLOCK000006', 66)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('UIA_EV_1_VOLTS', '0', '0', 'AIRLOCK000007', 67)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('UIA_EV_1_AMPS', '0', '0', 'AIRLOCK000008', 68)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('UIA_EV_2_VOLTS', '0', '0', 'AIRLOCK000009', 69)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('UIA_EV_2_AMPS', '0', '0', 'AIRLOCK000010', 70)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_AL1A4A_A_RPC_01_Depress_Pump_On_Off_Stat', '0', '0', 'AIRLOCK000047', 71)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Airlock_Depress_Pump_Power_Switch', '0', '0', 'AIRLOCK000048', 72)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Airlock_O2_Hi_P_Supply_Vlv_Actual_Posn', '0', '0', 'AIRLOCK000050', 73)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Airlock_O2_Lo_P_Supply_Vlv_Actual_Posn', '0', '0', 'AIRLOCK000051', 74)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Airlock_N2_Supply_Vlv_Actual_Posn', '0', '0', 'AIRLOCK000052', 75)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Airlock_CCAA_State', '0', '0', 'AIRLOCK000053', 76)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Airlock_PCA_Cabin_Pressure', '0', '0', 'AIRLOCK000054', 77)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Airlock_O2_Hi_P_Supply_Pressure', '0', '0', 'AIRLOCK000055', 78)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Airlock_O2_Lo_P_Supply_Pressure', '0', '0', 'AIRLOCK000056', 79)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Airlock_N2_Supply_Pressure', '0', '0', 'AIRLOCK000057', 80)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Node2_MTL_PPA_Avg_Accum_Qty', '0', '0', 'NODE2000001', 81)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Node2_LTL_PPA_Avg_Accum_Qty', '0', '0', 'NODE2000002', 82)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Node_2_CCAA_State', '0', '0', 'NODE2000003', 83)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Node2_LTL_TWMV_Out_Temp', '0', '0', 'NODE2000006', 84)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Node2_MTL_TWMV_Out_Temp', '0', '0', 'NODE2000007', 85)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Node_3_MCA_ppO2', '0', '0', 'NODE3000001', 86)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Node_3_MCA_ppN2', '0', '0', 'NODE3000002', 87)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Node_3_MCA_ppCO2', '0', '0', 'NODE3000003', 88)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Node_3_UPA_Current_State', '0', '0', 'NODE3000004', 89)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Node_3_UPA_WSTA_Qty_Ctrl_Pct', '0', '0', 'NODE3000005', 90)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Node_3_WPA_Process_Cmd_Status', '0', '0', 'NODE3000006', 91)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Node_3_WPA_Process_Step', '0', '0', 'NODE3000007', 92)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Node_3_WPA_Waste_Water_Qty_Ctrl', '0', '0', 'NODE3000008', 93)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Node_3_WPA_Water_Storage_Qty_Ctrl', '0', '0', 'NODE3000009', 94)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Node_3_OGA_Process_Cmd_Status', '0', '0', 'NODE3000010', 95)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Node_3_OGA_O2_Production_Rate', '0', '0', 'NODE3000011', 96)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Node3_MTL_TWMV_Out_Temp', '0', '0', 'NODE3000012', 97)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Node3_LTL_TWMV_Out_Temp', '0', '0', 'NODE3000013', 98)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Node3_MTL_PPA_Avg_Accum_Qty', '0', '0', 'NODE3000017', 99)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Node_3_CCAA_State', '0', '0', 'NODE3000018', 100)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Node3_LTL_PPA_Avg_Accum_Qty', '0', '0', 'NODE3000019', 101)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('DCSU_2A_PVCU_On_Off_V_Stat', '0', '0', 'P4000003', 102)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('DCSU_4A_PVCU_On_Off_V_Stat', '0', '0', 'P4000006', 103)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('DCSU_4B_RBI_6_Integ_I', '0', '0', 'P6000002', 104)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('DCSU_4B_PVCU_On_Off_V_Stat', '0', '0', 'P6000003', 105)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('DCSU_2B_PVCU_On_Off_V_Stat', '0', '0', 'P6000006', 106)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RSMCS_SM_KURS1_On', '0', '0', 'RUSSEG000002', 107)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RSMCS_SM_KURS2_On', '0', '0', 'RUSSEG000003', 108)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('SM_ECW_KURS_Fail', '0', '0', 'RUSSEG000004', 109)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RSMCS_SM_KURS_Rng', '0', '0', 'RUSSEG000005', 110)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RSMCS_SM_KURS_Vel', '0', '0', 'RUSSEG000006', 111)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('SM_KURS_P_Test_Mode_RS', '0', '0', 'RUSSEG000007', 112)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('SM_KURS_P_Capture_Signal_RS', '0', '0', 'RUSSEG000008', 113)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('SM_KURS_P_Target_Acquisition_Signal_RS', '0', '0', 'RUSSEG000009', 114)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('SM_KURS_P_Functional_Mode_Signal_RS', '0', '0', 'RUSSEG000010', 115)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('SM_KURS_P_In_Stand_by_Mode_RS', '0', '0', 'RUSSEG000011', 116)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RSMCS_SM_Dock_Contact', '0', '0', 'RUSSEG000012', 117)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RSMCS_SM_Forward_Port_Engaged', '0', '0', 'RUSSEG000013', 118)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RSMCS_SM_Aft_Port_Engaged', '0', '0', 'RUSSEG000014', 119)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RSMCS_SM_Nadir_Port_Engaged', '0', '0', 'RUSSEG000015', 120)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RSMCS_SM_FGB_Nadir_Port_Engaged', '0', '0', 'RUSSEG000016', 121)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RSMCS_SM_UDM_Nadir_Port_Engaged', '0', '0', 'RUSSEG000017', 122)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RSMCS_MRM1_Port_Engaged', '0', '0', 'RUSSEG000018', 123)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RSMCS_MRM2_Port_Engaged', '0', '0', 'RUSSEG000019', 124)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RSMCS_SM_ETOV_Hooks_Closed', '0', '0', 'RUSSEG000020', 125)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RSMCS_SM_Act_Att_Ref_Frame', '0', '0', 'RUSSEG000021', 126)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RSMCS_SM_RS_Is_Master', '0', '0', 'RUSSEG000022', 127)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RSMCS_SM_Ready_For_Indicator', '0', '0', 'RUSSEG000023', 128)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RSProp_SM_Thrstr_Mode_Terminated', '0', '0', 'RUSSEG000024', 129)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RSMCS_SM_SUDN_Mode', '0', '0', 'RUSSEG000025', 130)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('SARJ_Port_Commanded_Position', '0', '0', 'S0000005', 131)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_S01A_C_RPC_01_Ext_1_MDM_On_Off_Stat', '0', '0', 'S0000010', 132)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_S01A_C_RPC_16_S0_1_MDM_On_Off_Stat', '0', '0', 'S0000011', 133)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_S02B_C_RPC_01_Ext_2_MDM_On_Off_Stat', '0', '0', 'S0000012', 134)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_S02B_C_RPC_16_S0_2_MDM_On_Off_Stat', '0', '0', 'S0000013', 135)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_S11A_C_RPC_03_STR_MDM_On_Off_Stat', '0', '0', 'S1000006', 136)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_S11A_C_RPC_16_S1_1_MDM_On_Off_Stat', '0', '0', 'S1000007', 137)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_S12B_B_RPC_05_S1_2_MDM_On_Off_Stat', '0', '0', 'S1000008', 138)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('DCSU_1A_PVCU_On_Off_V_Stat', '0', '0', 'S4000003', 139)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('DCSU_3A_PVCU_On_Off_V_Stat', '0', '0', 'S4000006', 140)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('DCSU_3B_PVCU_On_Off_V_Stat', '0', '0', 'S6000003', 141)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('DCSU_1B_PVCU_On_Off_V_Stat', '0', '0', 'S6000006', 142)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Time of Occurrence', '0', '0', 'TIME_000001', 143)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Year of Occurrence', '0', '0', 'TIME_000002', 144)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_SEQ_CMG1_Online', '0', '0', 'USLAB000001', 145)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_SEQ_CMG2_Online', '0', '0', 'USLAB000002', 146)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_SEQ_CMG3_Online', '0', '0', 'USLAB000003', 147)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_SEQ_CMG4_Online', '0', '0', 'USLAB000004', 148)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CA_Num_CMGs_Online', '0', '0', 'USLAB000005', 149)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CA_Unlim_Cntl_Trq_InBody_X', '0', '0', 'USLAB000006', 150)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CA_Unlim_Cntl_Trq_InBody_Y', '0', '0', 'USLAB000007', 151)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CA_Unlim_Cntl_Trq_InBody_Z', '0', '0', 'USLAB000008', 152)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CA_CMG_Mom_Act_Mag', '0', '0', 'USLAB000009', 153)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CA_CMG_Mom_Act_Cap_Pct', '0', '0', 'USLAB000010', 154)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CA_Desat_Request_Inh', '0', '0', 'USLAB000011', 155)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_AD_Selected_Att_Source', '0', '0', 'USLAB000013', 156)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_AD_Selected_Rate_Source', '0', '0', 'USLAB000014', 157)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_SD_Selected_State_Source', '0', '0', 'USLAB000015', 158)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CA_Act_CCDB_Att_Cntl_Type', '0', '0', 'USLAB000016', 159)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CA_Act_CCDB_Att_Cntl_Ref_Frame', '0', '0', 'USLAB000017', 160)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_PS_Pointing_LVLH_Att_Quatrn_0', '0', '0', 'USLAB000018', 161)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_PS_Pointing_LVLH_Att_Quatrn_1', '0', '0', 'USLAB000019', 162)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_PS_Pointing_LVLH_Att_Quatrn_2', '0', '0', 'USLAB000020', 163)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_PS_Pointing_LVLH_Att_Quatrn_3', '0', '0', 'USLAB000021', 164)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CA_Att_Error_X', '0', '0', 'USLAB000022', 165)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CA_Att_Error_Y', '0', '0', 'USLAB000023', 166)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CA_Att_Error_Z', '0', '0', 'USLAB000024', 167)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_PS_Pointing_Current_Inert_Rate_Vector_X', '0', '0', 'USLAB000025', 168)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_PS_Pointing_Current_Inert_Rate_Vector_Y', '0', '0', 'USLAB000026', 169)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_PS_Pointing_Current_Inert_Rate_Vector_Z', '0', '0', 'USLAB000027', 170)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CA_Act_CCDB_AttQuatrn_0_Cmd', '0', '0', 'USLAB000028', 171)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CA_Act_CCDB_AttQuatrn_1_Cmd', '0', '0', 'USLAB000029', 172)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CA_Act_CCDB_AttQuatrn_2_Cmd', '0', '0', 'USLAB000030', 173)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CA_Act_CCDB_AttQuatrn_3_Cmd', '0', '0', 'USLAB000031', 174)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CA_CMG_Mom_Act_Cap', '0', '0', 'USLAB000038', 175)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_PS_Solar_Beta_Angle', '0', '0', 'USLAB000040', 176)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CA_Loss_Of_CMG_Att_Cntl_Latched_Caution', '0', '0', 'USLAB000041', 177)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CCS_Loss_of_ISS_Attitude_Control_Warning', '0', '0', 'USLAB000042', 178)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_GPS1_Operational_Status', '0', '0', 'USLAB000043', 179)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_GPS2_Operational_Status', '0', '0', 'USLAB000044', 180)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CMG1_SpinBrg_Temp1', '0', '0', 'USLAB000045', 181)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CMG2_SpinBrg_Temp1', '0', '0', 'USLAB000046', 182)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CMG3_SpinBrg_Temp1', '0', '0', 'USLAB000047', 183)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CMG4_SpinBrg_Temp1', '0', '0', 'USLAB000048', 184)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CMG1_SpinBrg_Temp2', '0', '0', 'USLAB000049', 185)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CMG2_SpinBrg_Temp2', '0', '0', 'USLAB000050', 186)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CMG3_SpinBrg_Temp2', '0', '0', 'USLAB000051', 187)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CMG4_SpinBrg_Temp2', '0', '0', 'USLAB000052', 188)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('LAB_MCA_ppO2', '0', '0', 'USLAB000053', 189)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('LAB_MCA_ppN2', '0', '0', 'USLAB000054', 190)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('LAB_MCA_ppCO2', '0', '0', 'USLAB000055', 191)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('LAB_LTL_PPA_Avg_Accum_Qty', '0', '0', 'USLAB000056', 192)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('LAB_MTL_PPA_Avg_Accum_Qty', '0', '0', 'USLAB000057', 193)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('LAB_PCA_Cabin_Pressure', '0', '0', 'USLAB000058', 194)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('LAB1P6_CCAA_In_T1', '0', '0', 'USLAB000059', 195)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('LAB_MTL_Regen_TWMV_Out_Temp', '0', '0', 'USLAB000060', 196)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('LAB_LTL_TWMV_Out_Temp', '0', '0', 'USLAB000061', 197)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('LAB_VRS_Vent_Vlv_Posn_Raw', '0', '0', 'USLAB000062', 198)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('LAB_VES_Vent_Vlv_Posn_Raw', '0', '0', 'USLAB000063', 199)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('LAB1P6_CCAA_State', '0', '0', 'USLAB000064', 200)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('LAB1S6_CCAA_State', '0', '0', 'USLAB000065', 201)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_LAD11B_A_RPC_07_CC_1_MDM_On_Off_Stat', '0', '0', 'USLAB000066', 202)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_LAD52B_A_RPC_03_CC_2_MDM_On_Off_Stat', '0', '0', 'USLAB000067', 203)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_LA1A4A_E_RPC_01_CC_3_MDM_On_Off_Stat', '0', '0', 'USLAB000068', 204)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_LAD11B_A_RPC_09_Int_1_MDM_On_Off_Stat', '0', '0', 'USLAB000069', 205)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_LAD52B_A_RPC_04_Int_2_MDM_On_Off_Stat', '0', '0', 'USLAB000070', 206)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_LAD11B_A_RPC_11_PL_1_MDM_On_Off_Stat', '0', '0', 'USLAB000071', 207)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_LAD22B_A_RPC_01_PL_2_MDM_On_Off_Stat', '0', '0', 'USLAB000072', 208)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_LA1B_B_RPC_14_GNC_1_MDM_On_Off_Stat', '0', '0', 'USLAB000073', 209)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_LA2B_E_RPC_03_GNC_2_MDM_On_Off_Stat', '0', '0', 'USLAB000074', 210)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_LAD11B_A_RPC_08_PMCU_1_MDM_On_Off_Stat', '0', '0', 'USLAB000075', 211)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_LAD52B_A_RPC_01_PMCU_2_MDM_On_Off_Stat', '0', '0', 'USLAB000076', 212)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_LA1B_B_RPC_09_LAB_1_MDM_On_Off_Stat', '0', '0', 'USLAB000077', 213)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_LA2B_E_RPC_04_LAB_2_MDM_On_Off_Stat', '0', '0', 'USLAB000078', 214)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_LA2B_E_RPC_13_LAB_3_MDM_On_Off_Stat', '0', '0', 'USLAB000079', 215)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_LA1B_D_RPC_01_LAB_FSEGF_Sys_Pwr_1_On_Off_Stat', '0', '0', 'USLAB000080', 216)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CA_AttMnvr_In_Progress', '0', '0', 'USLAB000081', 217)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Prim_CCS_MDM_Std_Cmd_Accept_Cnt', '0', '0', 'USLAB000082', 218)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Prim_CCS_MDM_Data_Load_Cmd_Accept_Cnt', '0', '0', 'USLAB000083', 219)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Coarse_Time', '0', '0', 'USLAB000084', 220)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Fine_Time', '0', '0', 'USLAB000085', 221)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Prim_CCS_MDM_PCS_Cnct_Cnt', '0', '0', 'USLAB000087', 222)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Ku_HRFM_VBSP_1_Activity_Indicator', '0', '0', 'USLAB000088', 223)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Ku_HRFM_VBSP_2_Activity_Indicator', '0', '0', 'USLAB000089', 224)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Ku_HRFM_VBSP_3_Activity_Indicator', '0', '0', 'USLAB000090', 225)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Ku_HRFM_VBSP_4_Activity_Indicator', '0', '0', 'USLAB000091', 226)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Audio_IAC1_Mode_Indication', '0', '0', 'USLAB000093', 227)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Audio_IAC2_Mode_Indication', '0', '0', 'USLAB000094', 228)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('VDS_Destination_9_Source_ID', '0', '0', 'USLAB000095', 229)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('VDS_Destination_13_Source_ID', '0', '0', 'USLAB000096', 230)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('VDS_Destination_14_Source_ID', '0', '0', 'USLAB000097', 231)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('VDS_Destination_29_Source_ID', '0', '0', 'USLAB000098', 232)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_LAD52B_A_RPC_08_UHF_SSSR_1_On_Off_Stat', '0', '0', 'USLAB000099', 233)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('RPCM_LA1B_H_RPC_04_UHF_SSSR_2_On_Off_Stat', '0', '0', 'USLAB000100', 234)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('UHF_Frame_Sync', '0', '0', 'USLAB000101', 235)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_SD_Selected_State_Time_Tag', '0', '0', 'USLAB000102', 236)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CMG1_IG_Vibration', '0', '0', 'Z1000001', 237)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CMG2_IG_Vibration', '0', '0', 'Z1000002', 238)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CMG3_IG_Vibration', '0', '0', 'Z1000003', 239)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CMG4_IG_Vibration', '0', '0', 'Z1000004', 240)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CMG1_SpinMtr_Current', '0', '0', 'Z1000005', 241)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CMG2_SpinMtr_Current', '0', '0', 'Z1000006', 242)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CMG3_SpinMtr_Current', '0', '0', 'Z1000007', 243)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CMG4_SpinMtr_Current', '0', '0', 'Z1000008', 244)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CMG1_Current_Wheel_Speed', '0', '0', 'Z1000009', 245)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CMG2_Current_Wheel_Speed', '0', '0', 'Z1000010', 246)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CMG3_Current_Wheel_Speed', '0', '0', 'Z1000011', 247)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('USGNC_CMG4_Current_Wheel_Speed', '0', '0', 'Z1000012', 248)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('eva_crew_1', '0', 'crew1', '0', 249)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('eva_crew_2', '0', 'crew2', '0', 250)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('us_eva_#', '0', '0', '0', 251)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('rs_eva_#', '0', '0', '0', 252)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('last_us_eva_duration', '0', '0', '0', 253)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('last_rs_eva_duration', '0', '0', '0', 254)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('Lightstreamer', '0', 'Unsubscribed', '0', 255)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('ClientStatus', '0', '0', '0', 256)");
logWrite("Successfully initialized SQlite database")

def staleTelemetry():
    c.execute("UPDATE telemetry SET Value = 'Unsubscribed' where Label = 'Lightstreamer'");

#----------------------------------Variables---------------------------------------------
LS_Subscription = False
isslocationsuccess = False
testfactor = -1
crew_mention= False
mimicbutton = False
fakeorbitboolean = False
demoboolean = False
zerocomplete = False
switchtofake = False
manualcontrol = False
startup = True
isscrew = 0
val = ""
lastsignal = 0
testvalue = 0
obtained_EVA_crew = False
unixconvert = time.gmtime(time.time())
EVAstartTime = float(unixconvert[7])*24+unixconvert[3]+float(unixconvert[4])/60+float(unixconvert[5])/3600
alternate = True
Beta4Bcontrol = False
Beta3Bcontrol = False
Beta2Bcontrol = False
Beta1Bcontrol = False
Beta4Acontrol = False
Beta3Acontrol = False
Beta2Acontrol = False
Beta1Acontrol = False
PSARJcontrol = False
SSARJcontrol = False
PTRRJcontrol = False
STRRJcontrol = False
stopAnimation = True
startingAnim = True
oldtdrs = "n/a"
runningDemo = False
logged = False
#-----------EPS Variables----------------------
EPSstorageindex = 0
channel1A_voltage = [154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1]
channel1B_voltage = [154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1]
channel2A_voltage = [154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1]
channel2B_voltage = [154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1]
channel3A_voltage = [154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1]
channel3B_voltage = [154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1]
channel4A_voltage = [154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1]
channel4B_voltage = [154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1, 154.1]
sizeX = 0.00
sizeY = 0.00
psarj2 = 1.0
ssarj2 = 1.0
new_x = 0
new_y = 0
new_x2 = 0
new_y2 = 0
aos = 0.00
los = 0.00
sgant_elevation = 0.00
sgant_xelevation = 0.00
sgant_elevation_old = -110.00
seconds2 = 260
oldLOS = 0.00
psarjmc = 0.00
ssarjmc = 0.00
ptrrjmc = 0.00
strrjmc = 0.00
beta1bmc = 0.00
beta1amc = 0.00
beta2bmc = 0.00
beta2amc = 0.00
beta3bmc = 0.00
beta3amc = 0.00
beta4bmc = 0.00
beta4amc = 0.00
US_EVAinProgress = False
leak_hold = False
firstcrossing = True
oldAirlockPump = 0.00
position_x = 0.00
position_y = 0.00
position_z = 0.00
velocity_x = 0.00
velocity_y = 0.00
velocity_z = 0.00
velocity = 0.00
altitude = 0.00
mass = 0.00
crewlockpres = 758
EVA_activities = False
repress = False
depress = False
seconds = 0
minutes = 0
hours = 0
leak_hold = False
EV1 = ""
EV2 = ""
numEVAs1 = ""
EVAtime_hours1 = ""
EVAtime_minutes1 = ""
numEVAs2 = ""
EVAtime_hours2 = ""
EVAtime_minutes2 = ""
holdstartTime = float(unixconvert[7])*24+unixconvert[3]+float(unixconvert[4])/60+float(unixconvert[5])/3600
eva = False
standby = False
prebreath1 = False
prebreath2 = False
depress1 = False
depress2 = False
leakhold = False
repress = False
TLE_acquired = False
stationmode = 0.00
tdrs = ""
EVA_picture_urls = []
urlindex = 0
module = ""
internet = False

class MainScreen(Screen):
    def changeManualControlBoolean(self, *args):
        global manualcontrol
        manualcontrol = args[0]

    def startDemo(*args):
        global p2, runningDemo
        if runningDemo == False:
            p2 = subprocess.Popen("/home/pi/Mimic/Pi/demoOrbit.sh")
            runningDemo = True
            logWrite("Successfully started Demo Orbit script")

    def stopDemo(*args):
        global p2, runningDemo
        try:
            p2.kill()
        except Exception:
            pass
        else:
            logWrite("Successfully stopped Demo Orbit script")
            runningDemo = False

    def startHTVDemo(*args):
        global p2, runningDemo
        if runningDemo == False:
            p2 = subprocess.Popen("/home/pi/Mimic/Pi/demoHTVOrbit.sh")
            runningDemo = True
            logWrite("Successfully started Demo HTV Orbit script")

    def stopHTVDemo(*args):
        global p2, runningDemo
        try:
            p2.kill()
        except Exception:
            pass
        else:
            logWrite("Successfully stopped Demo HTV Orbit script")
            runningDemo = False

    def startproc(*args):
        global p
        p = subprocess.Popen(["node", "/home/pi/Mimic/Pi/ISS_Telemetry.js"])
        logWrite("Successfully started ISS telemetry javascript")

    def killproc(*args):
        global p
        global p2
        try:
            p.kill()
            p2.kill()
        except Exception:
            pass
        os.system('rm /dev/shm/iss_telemetry.db') #delete sqlite database on exit, db is recreated each time to avoid concurrency issues
        staleTelemetry()
        logWrite("Successfully stopped ISS telemetry javascript and removed database")

class CalibrateScreen(Screen):

    def zeroJoints(self):
        self.changeBoolean(True)
        self.serialWrite("ZERO ")

class ManualControlScreen(Screen):
    def setActive(*args):
        global Beta4Bcontrol, Beta3Bcontrol, Beta2Bcontrol, Beta1Bcontrol, Beta4Acontrol, Beta3Acontrol, Beta2Acontrol, Beta1Acontrol, PSARJcontrol, SSARJcontrol, PTRRJcontrol, STRRJcontrol
        if str(args[1])=="Beta4B":
            Beta4Bcontrol = True
            Beta4Acontrol = False
            Beta3Bcontrol = False
            Beta3Acontrol = False
            Beta2Bcontrol = False
            Beta2Acontrol = False
            Beta1Bcontrol = False
            Beta1Acontrol = False
            PSARJcontrol = False
            SSARJcontrol = False
            PTRRJcontrol = False
            STRRJcontrol = False
        if str(args[1])=="Beta3B":
            Beta3Bcontrol = True
            Beta4Bcontrol = False
            Beta4Acontrol = False
            Beta3Acontrol = False
            Beta2Bcontrol = False
            Beta2Acontrol = False
            Beta1Bcontrol = False
            Beta1Acontrol = False
            PSARJcontrol = False
            SSARJcontrol = False
            PTRRJcontrol = False
            STRRJcontrol = False
        if str(args[1])=="Beta2B":
            Beta2Bcontrol = True
            Beta4Bcontrol = False
            Beta4Acontrol = False
            Beta3Bcontrol = False
            Beta3Acontrol = False
            Beta2Acontrol = False
            Beta1Bcontrol = False
            Beta1Acontrol = False
            PSARJcontrol = False
            SSARJcontrol = False
            PTRRJcontrol = False
            STRRJcontrol = False
        if str(args[1])=="Beta1B":
            Beta1Bcontrol = True
            Beta4Bcontrol = False
            Beta4Acontrol = False
            Beta3Bcontrol = False
            Beta3Acontrol = False
            Beta2Bcontrol = False
            Beta2Acontrol = False
            Beta1Acontrol = False
            PSARJcontrol = False
            SSARJcontrol = False
            PTRRJcontrol = False
            STRRJcontrol = False
        if str(args[1])=="Beta4A":
            Beta4Acontrol = True
            Beta4Bcontrol = False
            Beta3Bcontrol = False
            Beta3Acontrol = False
            Beta2Bcontrol = False
            Beta2Acontrol = False
            Beta1Bcontrol = False
            Beta1Acontrol = False
            PSARJcontrol = False
            SSARJcontrol = False
            PTRRJcontrol = False
            STRRJcontrol = False
        if str(args[1])=="Beta3A":
            Beta3Acontrol = True
            Beta4Bcontrol = False
            Beta4Acontrol = False
            Beta3Bcontrol = False
            Beta2Bcontrol = False
            Beta2Acontrol = False
            Beta1Bcontrol = False
            Beta1Acontrol = False
            PSARJcontrol = False
            SSARJcontrol = False
            PTRRJcontrol = False
            STRRJcontrol = False
        if str(args[1])=="Beta2A":
            Beta2Acontrol = True
            Beta4Bcontrol = False
            Beta4Acontrol = False
            Beta3Bcontrol = False
            Beta3Acontrol = False
            Beta2Bcontrol = False
            Beta1Bcontrol = False
            Beta1Acontrol = False
            PSARJcontrol = False
            SSARJcontrol = False
            PTRRJcontrol = False
            STRRJcontrol = False
        if str(args[1])=="Beta1A":
            Beta1Acontrol = True
            Beta4Bcontrol = False
            Beta4Acontrol = False
            Beta3Bcontrol = False
            Beta3Acontrol = False
            Beta2Bcontrol = False
            Beta2Acontrol = False
            Beta1Bcontrol = False
            PSARJcontrol = False
            SSARJcontrol = False
            PTRRJcontrol = False
            STRRJcontrol = False
        if str(args[1])=="PTRRJ":
            PTRRJcontrol = True
            Beta4Bcontrol = False
            Beta4Acontrol = False
            Beta3Bcontrol = False
            Beta3Acontrol = False
            Beta2Bcontrol = False
            Beta2Acontrol = False
            Beta1Bcontrol = False
            Beta1Acontrol = False
            PSARJcontrol = False
            SSARJcontrol = False
            STRRJcontrol = False
        if str(args[1])=="STRRJ":
            STRRJcontrol = True
            Beta4Bcontrol = False
            Beta4Acontrol = False
            Beta3Bcontrol = False
            Beta3Acontrol = False
            Beta2Bcontrol = False
            Beta2Acontrol = False
            Beta1Bcontrol = False
            Beta1Acontrol = False
            PSARJcontrol = False
            SSARJcontrol = False
            PTRRJcontrol = False
        if str(args[1])=="PSARJ":
            PSARJcontrol = True
            Beta4Bcontrol = False
            Beta4Acontrol = False
            Beta3Bcontrol = False
            Beta3Acontrol = False
            Beta2Bcontrol = False
            Beta2Acontrol = False
            Beta1Bcontrol = False
            Beta1Acontrol = False
            SSARJcontrol = False
            PTRRJcontrol = False
            STRRJcontrol = False
        if str(args[1])=="SSARJ":
            SSARJcontrol = True
            Beta4Bcontrol = False
            Beta4Acontrol = False
            Beta3Bcontrol = False
            Beta3Acontrol = False
            Beta2Bcontrol = False
            Beta2Acontrol = False
            Beta1Bcontrol = False
            Beta1Acontrol = False
            PSARJcontrol = False
            PTRRJcontrol = False
            STRRJcontrol = False

    def incrementActive(self, *args):
        global Beta4Bcontrol, Beta3Bcontrol, Beta2Bcontrol, Beta1Bcontrol, Beta4Acontrol, Beta3Acontrol, Beta2Acontrol, Beta1Acontrol, PSARJcontrol, SSARJcontrol, PTRRJcontrol, STRRJcontrol

        if Beta4Bcontrol:
            self.incrementBeta4B(args[0])
        if Beta3Bcontrol:
            self.incrementBeta3B(args[0])
        if Beta2Bcontrol:
            self.incrementBeta2B(args[0])
        if Beta1Bcontrol:
            self.incrementBeta1B(args[0])
        if Beta4Acontrol:
            self.incrementBeta4A(args[0])
        if Beta3Acontrol:
            self.incrementBeta3A(args[0])
        if Beta2Acontrol:
            self.incrementBeta2A(args[0])
        if Beta1Acontrol:
            self.incrementBeta1A(args[0])
        if PTRRJcontrol:
            self.incrementPTRRJ(args[0])
        if STRRJcontrol:
            self.incrementSTRRJ(args[0])
        if PSARJcontrol:
            self.incrementPSARJ(args[0])
        if SSARJcontrol:
            self.incrementSSARJ(args[0])

    def incrementPSARJ(self, *args):
        global psarjmc
        psarjmc += args[0]
        self.serialWrite("PSARJ=" + str(psarjmc) + " ")

    def incrementSSARJ(self, *args):
        global ssarjmc
        ssarjmc += args[0]
        self.serialWrite("SSARJ=" + str(ssarjmc) + " ")

    def incrementPTTRJ(self, *args):
        global ptrrjmc
        ptrrjmc += args[0]
        self.serialWrite("PTRRJ=" + str(ptrrjmc) + " ")

    def incrementSTRRJ(self, *args):
        global strrjmc
        strrjmc += args[0]
        self.serialWrite("STRRJ=" + str(strrjmc) + " ")

    def incrementBeta1B(self, *args):
        global beta1bmc
        beta1bmc += args[0]
        self.serialWrite("Beta1B=" + str(beta1bmc) + " ")

    def incrementBeta1A(self, *args):
        global beta1amc
        beta1amc += args[0]
        self.serialWrite("Beta1A=" + str(beta1amc) + " ")

    def incrementBeta2B(self, *args):
        global beta2bmc
        beta2bmc += args[0]
        self.serialWrite("Beta2B=" + str(beta2bmc) + " ")

    def incrementBeta2A(self, *args):
        global beta2amc
        beta2amc += args[0]
        self.serialWrite("Beta2A=" + str(beta2amc) + " ")

    def incrementBeta3B(self, *args):
        global beta3bmc
        beta3bmc += args[0]
        self.serialWrite("Beta3B=" + str(beta3bmc) + " ")

    def incrementBeta3A(self, *args):
        global beta3amc
        beta3amc += args[0]
        self.serialWrite("Beta3A=" + str(beta3amc) + " ")

    def incrementBeta4B(self, *args):
        global beta4bmc
        beta4bmc += args[0]
        self.serialWrite("Beta4B=" + str(beta4bmc) + " ")

    def incrementBeta4A(self, *args):
        global beta4amc
        beta4amc += args[0]
        self.serialWrite("Beta4A=" + str(beta4amc) + " ")

    def changeBoolean(self, *args):
        global manualcontrol
        manualcontrol = args[0]

    def send90(self, *args):
        self.serialWrite("Beta1A=90 ")
        self.serialWrite("Beta1B=90 ")
        self.serialWrite("Beta2A=90 ")
        self.serialWrite("Beta2B=90 ")
        self.serialWrite("Beta3A=90 ")
        self.serialWrite("Beta3B=90 ")
        self.serialWrite("Beta4A=90 ")
        self.serialWrite("Beta4B=90 ")
        self.serialWrite("PSARJ=90 ")
        self.serialWrite("SSARJ=90 ")
        self.serialWrite("PTRRJ=90 ")
        self.serialWrite("STRRJ=90 ")
        c.execute("UPDATE telemetry SET Value = '90' WHERE Label = 'beta1a'");
        c.execute("UPDATE telemetry SET Value = '90' WHERE Label = 'beta1b'");
        c.execute("UPDATE telemetry SET Value = '90' WHERE Label = 'beta2a'");
        c.execute("UPDATE telemetry SET Value = '90' WHERE Label = 'beta2b'");
        c.execute("UPDATE telemetry SET Value = '90' WHERE Label = 'beta3a'");
        c.execute("UPDATE telemetry SET Value = '90' WHERE Label = 'beta3b'");
        c.execute("UPDATE telemetry SET Value = '90' WHERE Label = 'beta4a'");
        c.execute("UPDATE telemetry SET Value = '90' WHERE Label = 'beta4b'");
        c.execute("UPDATE telemetry SET Value = '90' WHERE Label = 'psarj'");
        c.execute("UPDATE telemetry SET Value = '90' WHERE Label = 'ssarj'");
        c.execute("UPDATE telemetry SET Value = '90' WHERE Label = 'ptrrj'");
        c.execute("UPDATE telemetry SET Value = '90' WHERE Label = 'strrj'");

    def send0(self, *args):
        self.serialWrite("Beta1A=0 ")
        self.serialWrite("Beta1B=0 ")
        self.serialWrite("Beta2A=0 ")
        self.serialWrite("Beta2B=0 ")
        self.serialWrite("Beta3A=0 ")
        self.serialWrite("Beta3B=0 ")
        self.serialWrite("Beta4A=0 ")
        self.serialWrite("Beta4B=0 ")
        self.serialWrite("PSARJ=0 ")
        self.serialWrite("SSARJ=0 ")
        self.serialWrite("PTRRJ=0 ")
        self.serialWrite("STRRJ=0 ")
        c.execute("UPDATE telemetry SET Value = '0' WHERE Label = 'beta1a'");
        c.execute("UPDATE telemetry SET Value = '0' WHERE Label = 'beta1b'");
        c.execute("UPDATE telemetry SET Value = '0' WHERE Label = 'beta2a'");
        c.execute("UPDATE telemetry SET Value = '0' WHERE Label = 'beta2b'");
        c.execute("UPDATE telemetry SET Value = '0' WHERE Label = 'beta3a'");
        c.execute("UPDATE telemetry SET Value = '0' WHERE Label = 'beta3b'");
        c.execute("UPDATE telemetry SET Value = '0' WHERE Label = 'beta4a'");
        c.execute("UPDATE telemetry SET Value = '0' WHERE Label = 'beta4b'");
        c.execute("UPDATE telemetry SET Value = '0' WHERE Label = 'psarj'");
        c.execute("UPDATE telemetry SET Value = '0' WHERE Label = 'ssarj'");
        c.execute("UPDATE telemetry SET Value = '0' WHERE Label = 'ptrrj'");
        c.execute("UPDATE telemetry SET Value = '0' WHERE Label = 'strrj'");

    def serialWrite(self, *args):
        #logWrite("Function call - serial write")
        global SerialConnection1, SerialConnection2, SerialConnection3, SerialConnection4, SerialConnection5, ser, ser2, ser3, ser4, ser5
        #print str(*args)
        if SerialConnection1:
            #ser.write(str.encode(*args))
            try:
                ser.write(str.encode(*args))
            except Exception:
                ser = None
                SerialConnection1 = False
            #else:
            #    ser.write(str.encode(*args))
        if SerialConnection2:
            #ser2.write(str.encode(*args))
            try:
                ser2.write(str.encode(*args))
            except Exception:
                ser2 = None
                SerialConnection2 = False
            #else:
            #    ser.write(str.encode(*args))
        if SerialConnection3:
            #ser3.write(str.encode(*args))
            try:
                ser3.write(str.encode(*args))
            except Exception:
                ser3 = None
                SerialConnection3 = False
            #else:
            #    ser.write(str.encode(*args))
        if SerialConnection4:
            #ser4.write(str.encode(*args))
            try:
                ser4.write(str.encode(*args))
            except Exception:
                ser4 = None
                SerialConnection4 = False
            #else:
            #    ser.write(str.encode(*args))
        if SerialConnection5:
            #ser5.write(str.encode(*args))
            try:
                ser5.write(str.encode(*args))
            except Exception:
                ser5 = None
                SerialConnection5 = False
            #else:
            #    ser.write(str.encode(*args))


class FakeOrbitScreen(Screen):

    def changeDemoBoolean(self, *args):
        global demoboolean
        demoboolean = args[0]

    def HTVpopup(self, *args): #not fully working
        HTVpopup = Popup(title='HTV Berthing Orbit', content=Label(text='This will playback recorded data from when the Japanese HTV spacecraft berthed to the ISS. During berthing, the SARJs and nadir BGAs lock but the zenith BGAs autotrack'), text_size=self.size, size_hint=(0.5, 0.3), auto_dismiss=True)
        HTVpopup.text_size = self.size
        HTVpopup.open()

    def startDemo(*args):
        global p2, runningDemo
        if runningDemo == False:
            p2 = subprocess.Popen("/home/pi/Mimic/Pi/demoOrbit.sh")
            runningDemo = True

    def stopDemo(*args):
        global p2, runningDemo
        try:
            p2.kill()
        except Exception:
            pass
        else:
            runningDemo = False

    def startHTVDemo(*args):
        global p2, runningDemo
        if runningDemo == False:
            p2 = subprocess.Popen("/home/pi/Mimic/Pi/demoHTVOrbit.sh")
            runningDemo = True
            logWrite("Successfully started Demo HTV Orbit script")

    def stopHTVDemo(*args):
        global p2, runningDemo
        try:
            p2.kill()
        except Exception:
            pass
        else:
            logWrite("Successfully stopped Demo HTV Orbit script")
            runningDemo = False


    def serialWrite(self, *args):
        #logWrite("Function call - serial write")
        global SerialConnection1, SerialConnection2, SerialConnection3, SerialConnection4, SerialConnection5, ser, ser2, ser3, ser4, ser5

        if SerialConnection1:
            #ser.write(str.encode(*args))
            try:
                ser.write(str.encode(*args))
            except Exception:
                ser = None
                SerialConnection1 = False
            #else:
            #    ser.write(str.encode(*args))
        if SerialConnection2:
            #ser2.write(str.encode(*args))
            try:
                ser2.write(str.encode(*args))
            except Exception:
                ser2 = None
                SerialConnection2 = False
            #else:
            #    ser.write(str.encode(*args))
        if SerialConnection3:
            #ser3.write(str.encode(*args))
            try:
                ser3.write(str.encode(*args))
            except Exception:
                ser3 = None
                SerialConnection3 = False
            #else:
            #    ser.write(str.encode(*args))
        if SerialConnection4:
            #ser4.write(str.encode(*args))
            try:
                ser4.write(str.encode(*args))
            except Exception:
                ser4 = None
                SerialConnection4 = False
            #else:
            #    ser.write(str.encode(*args))
        if SerialConnection5:
            #ser5.write(str.encode(*args))
            try:
                ser5.write(str.encode(*args))
            except Exception:
                ser5 = None
                SerialConnection5 = False
            #else:
            #    ser.write(str.encode(*args))

class Settings_Screen(Screen, EventDispatcher):
    pass

class Orbit_Screen(Screen, EventDispatcher):
    pass

class ISS_Screen(Screen, EventDispatcher):
    signalcolor = ObjectProperty([1, 1, 1])
    def selectModule(*args):
        global module
        module = str(args[1])

class ECLSS_Screen(Screen, EventDispatcher):
    signalcolor = ObjectProperty([1, 1, 1])

class EPS_Screen(Screen, EventDispatcher):
    signalcolor = ObjectProperty([1, 1, 1])

class CT_Screen(Screen, EventDispatcher):
    signalcolor = ObjectProperty([1, 1, 1])

class CT_SASA_Screen(Screen, EventDispatcher):
    signalcolor = ObjectProperty([1, 1, 1])

class CT_Camera_Screen(Screen, EventDispatcher):
    signalcolor = ObjectProperty([1, 1, 1])

class CT_UHF_Screen(Screen, EventDispatcher):
    signalcolor = ObjectProperty([1, 1, 1])

class CT_SGANT_Screen(Screen, EventDispatcher):
    signalcolor = ObjectProperty([1, 1, 1])

class GNC_Screen(Screen, EventDispatcher):
    signalcolor = ObjectProperty([1, 1, 1])

class EVA_Main_Screen(Screen, EventDispatcher):
    signalcolor = ObjectProperty([1, 1, 1])
    pass

class EVA_US_Screen(Screen, EventDispatcher):
    signalcolor = ObjectProperty([1, 1, 1])
    pass

class EVA_RS_Screen(Screen, EventDispatcher):
    signalcolor = ObjectProperty([1, 1, 1])
    pass

class EVA_Pictures(Screen, EventDispatcher):
    pass

class TCS_Screen(Screen, EventDispatcher):
    signalcolor = ObjectProperty([1, 1, 1])

class RS_Screen(Screen, EventDispatcher):
    signalcolor = ObjectProperty([1, 1, 1])
    pass

class Crew_Screen(Screen, EventDispatcher):
    pass

class MimicScreen(Screen, EventDispatcher):
    signalcolor = ObjectProperty([1, 1, 1])
    def changeMimicBoolean(self, *args):
        global mimicbutton
        mimicbutton = args[0]

    def startproc(*args):
        global p
        print("mimic starting node")
        p = subprocess.Popen(["node", "/home/pi/Mimic/Pi/ISS_Telemetry.js"])

    def killproc(*args):
        global p
        global p2
        global c
        c.execute("INSERT OR IGNORE INTO telemetry VALUES('Lightstreamer', '0', 'Unsubscribed', '0', 0)");
        try:
            p.kill()
            p2.kill()
        except Exception:
            pass

class MainScreenManager(ScreenManager):
    pass

class MainApp(App):

    def build(self):
        global startup, ScreenList, stopAnimation

        self.main_screen = MainScreen(name = 'main')
        self.iss_screen = ISS_Screen(name = 'iss')
        self.eclss_screen = ECLSS_Screen(name = 'eclss')
        self.calibrate_screen = CalibrateScreen(name = 'calibrate')
        self.control_screen = ManualControlScreen(name = 'manualcontrol')
        self.orbit_screen = Orbit_Screen(name = 'orbit')
        self.fakeorbit_screen = FakeOrbitScreen(name = 'fakeorbit')
        self.mimic_screen = MimicScreen(name = 'mimic')
        self.eps_screen = EPS_Screen(name = 'eps')
        self.ct_screen = CT_Screen(name = 'ct')
        self.ct_sasa_screen = CT_SASA_Screen(name = 'ct_sasa')
        self.ct_uhf_screen = CT_UHF_Screen(name = 'ct_uhf')
        self.ct_camera_screen = CT_Camera_Screen(name = 'ct_camera')
        self.ct_sgant_screen = CT_SGANT_Screen(name = 'ct_sgant')
        self.gnc_screen = GNC_Screen(name = 'gnc')
        self.tcs_screen = TCS_Screen(name = 'tcs')
        self.crew_screen = Crew_Screen(name = 'crew')
        self.settings_screen = Settings_Screen(name = 'settings')
        self.us_eva = EVA_US_Screen(name='us_eva')
        self.rs_eva = EVA_RS_Screen(name='rs_eva')
        self.rs_screen = RS_Screen(name='rs')
        self.eva_main = EVA_Main_Screen(name='eva_main')
        self.eva_pictures = EVA_Pictures(name='eva_pictures')

        #Add all new telemetry screens to this list, this is used for the signal status icon and telemetry value colors
        ScreenList = ['tcs_screen', 'eps_screen', 'iss_screen', 'eclss_screen', 'ct_screen', 'ct_sasa_screen', 'ct_sgant_screen', 'ct_uhf_screen', 'ct_camera_screen', 'gnc_screen', 'orbit_screen', 'us_eva', 'rs_eva', 'eva_main', 'mimic_screen']

        root = MainScreenManager(transition=SwapTransition())
        root.add_widget(self.main_screen)
        root.add_widget(self.calibrate_screen)
        root.add_widget(self.control_screen)
        root.add_widget(self.mimic_screen)
        root.add_widget(self.fakeorbit_screen)
        root.add_widget(self.orbit_screen)
        root.add_widget(self.iss_screen)
        root.add_widget(self.eclss_screen)
        root.add_widget(self.eps_screen)
        root.add_widget(self.ct_screen)
        root.add_widget(self.ct_sasa_screen)
        root.add_widget(self.ct_uhf_screen)
        root.add_widget(self.ct_camera_screen)
        root.add_widget(self.ct_sgant_screen)
        root.add_widget(self.gnc_screen)
        root.add_widget(self.us_eva)
        root.add_widget(self.rs_eva)
        root.add_widget(self.rs_screen)
        root.add_widget(self.eva_main)
        root.add_widget(self.eva_pictures)
        root.add_widget(self.tcs_screen)
        root.add_widget(self.crew_screen)
        root.add_widget(self.settings_screen)
        root.current = 'main' #change this back to main when done with eva setup

        Clock.schedule_interval(self.update_labels, 1)
        Clock.schedule_interval(self.animate3, 0.1)
        Clock.schedule_interval(self.orbitUpdate, 1)
        Clock.schedule_interval(self.checkCrew, 600)
        if startup:
            startup = False

        Clock.schedule_once(self.checkCrew, 30)
        Clock.schedule_once(self.getTLE, 40) #uncomment when internet works again
        Clock.schedule_interval(self.getTLE, 300)
        Clock.schedule_interval(self.check_internet, 1)
        Clock.schedule_interval(self.check_serial, 1)
        return root

    def check_serial(self, dt):
        global SerialConnection1, SerialConnection2, SerialConnection3, SerialConnection4, SerialConnection5, ser, ser2, ser3, ser4, ser5

        if ser == None:
            try:
                ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0)
            except Exception as e:
                #logWrite("Warning - Serial Connection ACM0 not found")
                print(e)
                SerialConnection1 = False
                ser = None
            else:
                SerialConnection1 = True
                logWrite("Successful connection to Serial on ACMO")
                print(str(ser))
        else:
            try:
                ser.write(str.encode("test"))
            except Exception as e:
                print(e)
                SerialConnection1 = False
                ser = None
            else:
                SerialConnection1 = True

        if ser2 == None:
            try:
                ser2 = serial.Serial('/dev/ttyACM1', 9600, timeout=0)
            except Exception:
                #logWrite("Warning - Serial Connection ACM1 not found")
                SerialConnection2 = False
                ser2 = None
            else:
                SerialConnection2 = True
                logWrite("Successful connection to Serial on ACM1")
                print(str(ser2))
        else:
            try:
                ser2.write(str.encode("test"))
            except Exception:
                SerialConnection2 = False
                ser2 = None
            else:
                SerialConnection2 = True

        if ser3 == None:
            try:
                ser3 = serial.Serial('/dev/ttyACM2', 9600, timeout=0)
            except Exception:
                #logWrite("Warning - Serial Connection ACM2 not found")
                SerialConnection3 = False
                ser3 = None
            else:
                SerialConnection3 = True
                logWrite("Successful connection to Serial on ACM2")
                print(str(ser3))
        else:
            try:
                ser3.write(str.encode("test"))
            except Exception:
                SerialConnection3 = False
                ser3 = None
            else:
                SerialConnection3 = True

        if ser4 == None:
            try:
                ser4 = serial.Serial('/dev/ttyAMA00', 9600, timeout=0)
            except Exception:
                #logWrite("Warning - Serial Connection AMA00 not found")
                SerialConnection4 = False
                ser4 = None
            else:
                SerialConnection4 = True
                logWrite("Successful connection to Serial on AMA0O")
                print(str(ser4))
        else:
            try:
                ser4.write(str.encode("test"))
            except Exception:
                SerialConnection4 = False
                ser4 = None
            else:
                SerialConnection4 = True

        if ser5 == None:
            try:
                ser5 = serial.Serial('/dev/ttyUSB0', 9600, timeout=0)
            except Exception:
                #logWrite("Warning - Serial Connection USB0 not found")
                SerialConnection5 = False
                ser5 = None
            else:
                SerialConnection5 = True
                logWrite("Successful connection to Serial on USBO")
                print(str(ser5))
        else:
            try:
                ser5.write(str.encode("test"))
            except Exception:
                SerialConnection5 = False
                ser5 = None
            else:
                SerialConnection5 = True

    def check_internet(self, dt):
        global internet

        def on_success(req, result):
            global internet
            #print "internet success"
            internet = True

        def on_redirect(req, result):
            global internet
            #print "internet redirect"
            internet = True

        def on_failure(req, result):
            global internet
            #print "internet failure"
            internet = False

        def on_error(req, result):
            global internet
            #print "internet error"
            internet = False

        req = UrlRequest("http://google.com", on_success, on_redirect, on_failure, on_error, timeout=1)

    def deleteURLPictures(self, dt):
        logWrite("Function call - deleteURLPictures")
        global EVA_picture_urls
        del EVA_picture_urls[:]
        EVA_picture_urls[:] = []

    def changePictures(self, dt):
        logWrite("Function call - changeURLPictures")
        global EVA_picture_urls
        global urlindex
        urlsize = len(EVA_picture_urls)

        if urlsize > 0:
            self.us_eva.ids.EVAimage.source = EVA_picture_urls[urlindex]
            self.eva_pictures.ids.EVAimage.source = EVA_picture_urls[urlindex]

        urlindex = urlindex + 1
        if urlindex > urlsize-1:
            urlindex = 0

    def check_EVA_stats(self, lastname1, firstname1, lastname2, firstname2):
        global numEVAs1, EVAtime_hours1, EVAtime_minutes1, numEVAs2, EVAtime_hours2, EVAtime_minutes2, EV1, EV2
        logWrite("Function call - check EVA stats")
        eva_url = 'http://www.spacefacts.de/eva/e_eva_az.htm'

        def on_success(req, result):
            logWrite("Check EVA Stats - Successs")
            soup = BeautifulSoup(result, 'html.parser') #using bs4 to parse website
            numEVAs1 = 0
            EVAtime_hours1 = 0
            EVAtime_minutes1 = 0
            numEVAs2 = 0
            EVAtime_hours2 = 0
            EVAtime_minutes2 = 0

            tabletags = soup.find_all("td")
            for tag in tabletags:
                if  lastname1 in tag.text:
                    if firstname1 in tag.find_next_sibling("td").text:
                        numEVAs1 = tag.find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").text
                        EVAtime_hours1 = int(tag.find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").text)
                        EVAtime_minutes1 = int(tag.find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").text)
                        EVAtime_minutes1 += (EVAtime_hours1 * 60)

            for tag in tabletags:
                if lastname2 in tag.text:
                    if firstname2 in tag.find_next_sibling("td").text:
                        numEVAs2 = tag.find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").text
                        EVAtime_hours2 = int(tag.find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").text)
                        EVAtime_minutes2 = int(tag.find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").text)
                        EVAtime_minutes2 += (EVAtime_hours2 * 60)

            EV1_EVA_number = numEVAs1
            EV1_EVA_time  = EVAtime_minutes1
            EV2_EVA_number = numEVAs2
            EV2_EVA_time  = EVAtime_minutes2

            EV1_minutes = str(EV1_EVA_time%60).zfill(2)
            EV2_minutes = str(EV2_EVA_time%60).zfill(2)
            EV1_hours = int(EV1_EVA_time/60)
            EV2_hours = int(EV2_EVA_time/60)

            self.us_eva.ids.EV1.text = str(EV1) + " (EV1):"
            self.us_eva.ids.EV2.text = str(EV2) + " (EV2):"
            self.us_eva.ids.EV1_EVAnum.text = "Number of EVAs = " + str(EV1_EVA_number)
            self.us_eva.ids.EV2_EVAnum.text = "Number of EVAs = " + str(EV2_EVA_number)
            self.us_eva.ids.EV1_EVAtime.text = "Total EVA Time = " + str(EV1_hours) + "h " + str(EV1_minutes) + "m"
            self.us_eva.ids.EV2_EVAtime.text = "Total EVA Time = " + str(EV2_hours) + "h " + str(EV2_minutes) + "m"

        def on_redirect(req, result):
            logWrite("Warning - EVA stats failure (redirect)")

        def on_failure(req, result):
            logWrite("Warning - EVA stats failure (url failure)")

        def on_error(req, result):
            logWrite("Warning - EVA stats failure (url error)")
        
        #obtain eva statistics web page for parsing
        req = UrlRequest(eva_url, on_success, on_redirect, on_failure, on_error, timeout=1)

    def flashUS_EVAbutton(self, instance):
        logWrite("Function call - flashUS_EVA")

        self.eva_main.ids.US_EVA_Button.background_color = (0, 0, 1, 1)
        def reset_color(*args):
            self.eva_main.ids.US_EVA_Button.background_color = (1, 1, 1, 1)
        Clock.schedule_once(reset_color, 0.5)

    def flashRS_EVAbutton(self, instance):
        logWrite("Function call - flashRS_EVA")

        self.eva_main.ids.RS_EVA_Button.background_color = (0, 0, 1, 1)
        def reset_color(*args):
            self.eva_main.ids.RS_EVA_Button.background_color = (1, 1, 1, 1)
        Clock.schedule_once(reset_color, 0.5)

    def flashEVAbutton(self, instance):
        logWrite("Function call - flashEVA")

        self.mimic_screen.ids.EVA_button.background_color = (0, 0, 1, 1)
        def reset_color(*args):
            self.mimic_screen.ids.EVA_button.background_color = (1, 1, 1, 1)
        Clock.schedule_once(reset_color, 0.5)

    def EVA_clock(self, dt):
        global seconds, minutes, hours, EVAstartTime
        unixconvert = time.gmtime(time.time())
        currenthours = float(unixconvert[7])*24+unixconvert[3]+float(unixconvert[4])/60+float(unixconvert[5])/3600
        difference = (currenthours-EVAstartTime)*3600
        minutes, seconds = divmod(difference, 60)
        hours, minutes = divmod(minutes, 60)

        hours = int(hours)
        minutes = int(minutes)
        seconds = int(seconds)

        self.us_eva.ids.EVA_clock.text =(str(hours) + ":" + str(minutes).zfill(2) + ":" + str(int(seconds)).zfill(2))
        self.us_eva.ids.EVA_clock.color = 0.33, 0.7, 0.18

    def animate(self, instance):
        global new_x2, new_y2
        self.main_screen.ids.ISStiny2.size_hint = 0.07, 0.07
        new_x2 = new_x2+0.007
        new_y2 = (math.sin(new_x2*30)/18)+0.75
        if new_x2 > 1:
            new_x2 = new_x2-1.0
        self.main_screen.ids.ISStiny2.pos_hint = {"center_x": new_x2, "center_y": new_y2}

    def animate3(self, instance):
        global new_x, new_y, sizeX, sizeY, startingAnim
        if new_x<0.886:
            new_x = new_x+0.007
            new_y = (math.sin(new_x*30)/18)+0.75
            self.main_screen.ids.ISStiny.pos_hint = {"center_x": new_x, "center_y": new_y}
        else:
            if sizeX <= 0.15:
                sizeX = sizeX + 0.01
                sizeY = sizeY + 0.01
                self.main_screen.ids.ISStiny.size_hint = sizeX, sizeY
            else:
                if startingAnim:
                    Clock.schedule_interval(self.animate, 0.1)
                    startingAnim = False

    def serialWrite(self, *args):
        #logWrite("Function call - serial write")
        global SerialConnection1, SerialConnection2, SerialConnection3, SerialConnection4, SerialConnection5, ser, ser2, ser3, ser4, ser5

        if SerialConnection1:
            #ser.write(str.encode(*args))
            try:
                ser.write(str.encode(*args))
            except Exception:
                ser = None
                SerialConnection1 = False
            #else:
            #    ser.write(str.encode(*args))
        if SerialConnection2:
            #ser2.write(str.encode(*args))
            try:
                ser2.write(str.encode(*args))
            except Exception:
                ser2 = None
                SerialConnection2 = False
            #else:
            #    ser.write(str.encode(*args))
        if SerialConnection3:
            #ser3.write(str.encode(*args))
            try:
                ser3.write(str.encode(*args))
            except Exception:
                ser3 = None
                SerialConnection3 = False
            #else:
            #    ser.write(str.encode(*args))
        if SerialConnection4:
            #ser4.write(str.encode(*args))
            try:
                ser4.write(str.encode(*args))
            except Exception:
                ser4 = None
                SerialConnection4 = False
            #else:
            #    ser.write(str.encode(*args))
        if SerialConnection5:
            #ser5.write(str.encode(*args))
            try:
                ser5.write(str.encode(*args))
            except Exception:
                ser5 = None
                SerialConnection5 = False
            #else:
            #    ser.write(str.encode(*args))

    def changeColors(self, *args):   #this function sets all labels on mimic screen to a certain color based on signal status
        #the signalcolor is a kv property that will update all signal status dependant values to whatever color is received by this function
        global ScreenList

        for x in ScreenList:
            getattr(self, x).signalcolor = args[0], args[1], args[2]

    def changeManualControlBoolean(self, *args):
        global manualcontrol
        manualcontrol = args[0]

    def orbitUpdate(self, dt):
        global overcountry, tle_rec, line1, line2, TLE_acquired, sgant_elevation, sgant_elevation_old, sgant_xelevation, aos, oldtdrs, tdrs, logged
        def scaleLatLon(latitude, longitude):
            #converting lat lon to x, y for orbit map
            fromLatSpan = 180.0
            fromLonSpan = 360.0
            toLatSpan = 0.598
            toLonSpan = 0.716
            valueLatScaled = (float(latitude)+90.0)/float(fromLatSpan)
            valueLonScaled = (float(longitude)+180.0)/float(fromLonSpan)
            newLat = (0.265) + (valueLatScaled * toLatSpan)
            newLon = (0.14) + (valueLonScaled * toLonSpan)
            return {'newLat': newLat, 'newLon': newLon}

        def toYearFraction(date):
            def sinceEpoch(date): # returns seconds since epoch
                return time.mktime(date.timetuple())
            s = sinceEpoch
            year = date.year
            startOfThisYear = datetime(year=year, month=1, day=1)
            startOfNextYear = datetime(year=year+1, month=1, day=1)
            yearElapsed = s(date) - s(startOfThisYear)
            yearDuration = s(startOfNextYear) - s(startOfThisYear)
            fraction = yearElapsed/yearDuration
            if float(fraction*365.24) < 100:
                current_epoch = str(date.year)[2:] + "0" + str(fraction*365.24)
            else:
                current_epoch = str(date.year)[2:] + str(fraction*365.24)
            return current_epoch

        #draw the TDRS satellite locations
        self.orbit_screen.ids.TDRSe.pos_hint = {"center_x": scaleLatLon(0, -41)['newLon'], "center_y": scaleLatLon(0, -41)['newLat']}
        self.orbit_screen.ids.TDRSeLabel.pos_hint = {"center_x": scaleLatLon(0, -41)['newLon']+0.06, "center_y": scaleLatLon(0, -41)['newLat']}
        self.orbit_screen.ids.TDRSw.pos_hint = {"center_x": scaleLatLon(0, -174)['newLon'], "center_y": scaleLatLon(0, -174)['newLat']}
        self.orbit_screen.ids.TDRSwLabel.pos_hint = {"center_x": scaleLatLon(0, -174)['newLon']+0.06, "center_y": scaleLatLon(0, -174)['newLat']}
        self.orbit_screen.ids.TDRSz.pos_hint = {"center_x": scaleLatLon(0, 85)['newLon'], "center_y": scaleLatLon(0, 85)['newLat']}
        self.orbit_screen.ids.TDRSzLabel.pos_hint = {"center_x": scaleLatLon(0, 85)['newLon']+0.05, "center_y": scaleLatLon(0, 85)['newLat']}
        self.orbit_screen.ids.ZOE.pos_hint = {"center_x": scaleLatLon(0, 77)['newLon'], "center_y": scaleLatLon(0, 77)['newLat']}
        self.orbit_screen.ids.ZOElabel.pos_hint = {"center_x": scaleLatLon(0, 77)['newLon'], "center_y": scaleLatLon(0, 77)['newLat']+0.1}

        if TLE_acquired:
            tle_rec.compute()
            #------------------Latitude/Longitude Stuff---------------------------
            latitude = tle_rec.sublat
            longitude = tle_rec.sublong
            latitude = float(str(latitude).split(':')[0]) + float(str(latitude).split(':')[1])/60 + float(str(latitude).split(':')[2])/3600
            longitude = float(str(longitude).split(':')[0]) + float(str(longitude).split(':')[1])/60 + float(str(longitude).split(':')[2])/3600
            coordinates = ((latitude, longitude), (latitude, longitude))

            if float(aos) == 0.00 and not logged:
                sgantlog.write(str(datetime.utcnow()))
                sgantlog.write(' ')
                sgantlog.write(str(sgant_elevation))
                sgantlog.write(' ')
                sgantlog.write(str(sgant_xelevation))
                sgantlog.write(' ')
                sgantlog.write(str(latitude))
                sgantlog.write(' ')
                sgantlog.write(str(longitude))
                #sgantlog.write(' ')
                #sgantlog.write(str(aos))
                sgantlog.write('\n')
                logged = True

            if logged and aos == 1.00:
                logged = False

            self.orbit_screen.ids.OrbitISStiny.pos_hint = {"center_x": scaleLatLon(latitude, longitude)['newLon'], "center_y": scaleLatLon(latitude, longitude)['newLat']}
            self.orbit_screen.ids.latitude.text = str("{:.2f}".format(latitude))
            self.orbit_screen.ids.longitude.text = str("{:.2f}".format(longitude))

            #need to determine which tdrs is being used based on longitude and sgant elevation
            #TDRSw = -174
            #TDRSe = -41
            #TDRSz = 85
            tdrs = "n/a"
            self.ct_sgant_screen.ids.tdrs_east.angle = (-1*longitude)-41
            self.ct_sgant_screen.ids.tdrs_z.angle = ((-1*longitude)-41)+126
            self.ct_sgant_screen.ids.tdrs_west.angle = ((-1*longitude)-41)-133

            if longitude > 90 and sgant_elevation < -10 and float(aos) == 1.0:
                self.ct_sgant_screen.ids.tdrs_label.text = "TDRS-West"
                tdrs = "west"
            elif longitude > 60 and longitude < 140 and sgant_elevation > -10 and float(aos) == 1.0:
                self.ct_sgant_screen.ids.tdrs_label.text = "TDRS-Z"
                tdrs = "z"
            elif longitude > 0 and longitude <= 90 and sgant_elevation < -10 and float(aos) == 1.0:
                self.ct_sgant_screen.ids.tdrs_label.text = "TDRS-Z"
                tdrs = "z"
            elif longitude > -80 and longitude <= 60 and sgant_elevation > -10 and float(aos) == 1.0:
                self.ct_sgant_screen.ids.tdrs_label.text = "TDRS-East"
                tdrs = "east"
            elif longitude > -160 and longitude <= 0 and sgant_elevation < -10 and float(aos) == 1.0:
                self.ct_sgant_screen.ids.tdrs_label.text = "TDRS-East"
                tdrs = "east"
            elif ((longitude >= -180 and longitude <= -80) or (longitude > 140)) and sgant_elevation > -40 and float(aos) == 1.0:
                self.ct_sgant_screen.ids.tdrs_label.text = "TDRS-West"
                tdrs = "west"
            else:
                self.ct_sgant_screen.ids.tdrs_label.text = ""
                tdrs = "----"

            if tdrs == "west":
                self.orbit_screen.ids.TDRSwLabel.color = 1, 0, 1
                self.orbit_screen.ids.TDRSeLabel.color = 1, 1, 1
                self.orbit_screen.ids.TDRSzLabel.color = 1, 1, 1
                self.orbit_screen.ids.TDRSw.col = (1, 0, 1)
                self.orbit_screen.ids.TDRSe.col = (1, 1, 1)
                self.orbit_screen.ids.TDRSz.col = (1, 1, 1)
                self.orbit_screen.ids.ZOElabel.color = 1, 1, 1
            elif tdrs == "east":
                self.orbit_screen.ids.TDRSwLabel.color = 1, 1, 1
                self.orbit_screen.ids.TDRSeLabel.color = 1, 0, 1
                self.orbit_screen.ids.TDRSzLabel.color = 1, 1, 1
                self.orbit_screen.ids.TDRSw.col = (1, 1, 1)
                self.orbit_screen.ids.TDRSe.col = (1, 0, 1)
                self.orbit_screen.ids.TDRSz.col = (1, 1, 1)
                self.orbit_screen.ids.ZOElabel.color = 1, 1, 1
            elif tdrs == "z":
                self.orbit_screen.ids.TDRSwLabel.color = 1, 1, 1
                self.orbit_screen.ids.TDRSeLabel.color = 1, 1, 1
                self.orbit_screen.ids.TDRSzLabel.color = 1, 0, 1
                self.orbit_screen.ids.TDRSw.col = (1, 1, 1)
                self.orbit_screen.ids.TDRSe.col = (1, 1, 1)
                self.orbit_screen.ids.TDRSz.col = (1, 0, 1)
                self.orbit_screen.ids.ZOElabel.color = 1, 1, 1
            else:
                self.orbit_screen.ids.TDRSwLabel.color = 1, 1, 1
                self.orbit_screen.ids.TDRSeLabel.color = 1, 1, 1
                self.orbit_screen.ids.TDRSzLabel.color = 1, 1, 1
                self.orbit_screen.ids.TDRSw.col = (1, 1, 1)
                self.orbit_screen.ids.TDRSe.col = (1, 1, 1)
                self.orbit_screen.ids.TDRSz.col = (1, 1, 1)
                self.orbit_screen.ids.ZOElabel.color = 1, 1, 1

            if aos == 0.00 and longitude > 60 and longitude < 100 and tdrs == "----":
                self.orbit_screen.ids.TDRSwLabel.color = 1, 1, 1
                self.orbit_screen.ids.TDRSeLabel.color = 1, 1, 1
                self.orbit_screen.ids.TDRSzLabel.color = 1, 1, 1
                self.orbit_screen.ids.TDRSw.col = (1, 1, 1)
                self.orbit_screen.ids.TDRSe.col = (1, 1, 1)
                self.orbit_screen.ids.TDRSz.col = (1, 1, 1)
                self.orbit_screen.ids.ZOElabel.color = 1, 0, 0

            #if tdrs != oldtdrs and float(aos) == 1.0:
            #    oldtdrs = tdrs
            #    sgantlog.write(str(datetime.utcnow()))
            #    sgantlog.write(' ')
            #    sgantlog.write(str(sgant_elevation))
            #    sgantlog.write(' ')
            #    sgantlog.write(str(longitude))
            #    sgantlog.write(' ')
            #    sgantlog.write(str(tdrs))
            #    sgantlog.write(' ')
            #    sgantlog.write('\n')

            #------------------Orbit Stuff---------------------------
            now = datetime.utcnow()
            mins = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
            orbits_today = math.floor((float(mins)/60)/90)
            self.orbit_screen.ids.dailyorbit.text = str(int(orbits_today)) #display number of orbits since utc midnight

            time_since_epoch = float(toYearFraction(datetime.utcnow())) - float(line1[22:36])
            totalorbits = int(line2[68:72]) + 100000 + int(float(time_since_epoch)*24/1.5) #add number of orbits since the tle was generated
            self.orbit_screen.ids.totalorbits.text = str(totalorbits) #display number of orbits since utc midnight
            #------------------ISS Pass Detection---------------------------
            location = ephem.Observer()
            location.lon         = '-95:21:59' #will next to make these an input option
            location.lat         = '29:45:43'
            location.elevation   = 10
            location.name        = 'location'
            location.horizon    = '10'
            location.date = datetime.utcnow()
            #use location to draw dot on orbit map
            mylatitude = float(str(location.lat).split(':')[0]) + float(str(location.lat).split(':')[1])/60 + float(str(location.lat).split(':')[2])/3600
            mylongitude = float(str(location.lon).split(':')[0]) + float(str(location.lon).split(':')[1])/60 + float(str(location.lon).split(':')[2])/3600
            self.orbit_screen.ids.mylocation.pos_hint = {"center_x": scaleLatLon(mylatitude, mylongitude)['newLon'], "center_y": scaleLatLon(mylatitude, mylongitude)['newLat']}

            tle_rec.compute(location) #compute tle propagation based on provided location
            nextpassinfo = location.next_pass(tle_rec)
            #print nextpassinfo #might need to add try block to next line
            if nextpassinfo[0] == None:
                self.orbit_screen.ids.iss_next_pass1.text = "n/a"
                self.orbit_screen.ids.iss_next_pass2.text = "n/a"
                self.orbit_screen.ids.countdown.text = "n/a"
            else:
                nextpassdatetime = datetime.strptime(str(nextpassinfo[0]), '%Y/%m/%d %H:%M:%S') #convert to datetime object for timezone conversion
                nextpassinfo_format = nextpassdatetime.replace(tzinfo=pytz.utc)
                localtimezone = pytz.timezone('America/Chicago')
                localnextpass = nextpassinfo_format.astimezone(localtimezone)
                self.orbit_screen.ids.iss_next_pass1.text = str(localnextpass).split()[0] #display next pass time
                self.orbit_screen.ids.iss_next_pass2.text = str(localnextpass).split()[1].split('-')[0] #display next pass time
                timeuntilnextpass = nextpassinfo[0] - location.date
                #print timeuntilnextpass
                nextpasshours = timeuntilnextpass*24.0
                nextpassmins = (nextpasshours-math.floor(nextpasshours))*60
                nextpassseconds = (nextpassmins-math.floor(nextpassmins))*60
                self.orbit_screen.ids.countdown.text = str("{:.0f}".format(math.floor(nextpasshours))) + ":" + str("{:.0f}".format(math.floor(nextpassmins))) + ":" + str("{:.0f}".format(math.floor(nextpassseconds))) #display time until next pass

    def getTLE(self, *args):
        global tle_rec, line1, line2, TLE_acquired
        iss_tle_url =  'https://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/orbit/ISS/SVPOST.html'
        
        def on_success(req, data): #if TLE data is successfully received, it is processed here
            global tle_rec, line1, line2, TLE_acquired
            def process_tag_text(tag_text): #this function splits up the data received into proper TLE format
                firstTLE = True
                marker = 'TWO LINE MEAN ELEMENT SET'
                text = iter(tag_text.split('\n'))
                for line in text:
                    if (marker in line) and firstTLE:
                        firstTLE = False
                        next(text)
                        results.append('\n'.join(
                            (next(text), next(text), next(text))))
                return results
            logWrite("ISS TLE - Successfully fetched TLE page")
            soup = BeautifulSoup(data, 'html.parser')
            body = soup.find_all("pre")
            results = []
            for tag in body:
                if "ISS" in tag.text:
                    results.extend(process_tag_text(tag.text))

            if len(results) > 0:
                parsed = str(results[0]).split('\n')
                line1 = parsed[1]
                line2 = parsed[2]
                print(line1)
                print(line2)
                tle_rec = ephem.readtle("ISS (ZARYA)", str(line1), str(line2))
                TLE_acquired = True
                print("TLE Success!")
            else:
                print("TLE not acquired")
                TLE_acquired = False

        def on_redirect(req, result):
            logWrite("Warning - Get TLE failure (redirect)")

        def on_failure(req, result):
            logWrite("Warning - Get TLE failure (url failure)")

        def on_error(req, result):
            logWrite("Warning - Get TLE failure (url error)")
        
        req = UrlRequest(iss_tle_url, on_success, on_redirect, on_failure, on_error, timeout=1)

    def checkCrew(self, dt):
        iss_crew_url = 'http://www.howmanypeopleareinspacerightnow.com/peopleinspace.json'
        urlsuccess = False

        def on_success(req, data):
            logWrite("Successfully fetched crew JSON")
            isscrew = 0
            crewmember = ['', '', '', '', '', '', '', '', '', '', '', '']
            crewmemberbio = ['', '', '', '', '', '', '', '', '', '', '', '']
            crewmembertitle = ['', '', '', '', '', '', '', '', '', '', '', '']
            crewmemberdays = ['', '', '', '', '', '', '', '', '', '', '', '']
            crewmemberpicture = ['', '', '', '', '', '', '', '', '', '', '', '']
            crewmembercountry = ['', '', '', '', '', '', '', '', '', '', '', '']
            now = datetime.utcnow()
            number_of_space = int(data['number'])
            for num in range(1, number_of_space+1):
                if(str(data['people'][num-1]['location']) == str("International Space Station")):
                    crewmember[isscrew] = str(data['people'][num-1]['name']) #.encode('utf-8')
                    crewmemberbio[isscrew] = str(data['people'][num-1]['bio'])
                    crewmembertitle[isscrew] = str(data['people'][num-1]['title'])
                    datetime_object = datetime.strptime(str(data['people'][num-1]['launchdate']), '%Y-%m-%d')
                    previousdays = int(data['people'][num-1]['careerdays'])
                    totaldaysinspace = str(now-datetime_object)
                    d_index = totaldaysinspace.index('d')
                    crewmemberdays[isscrew] = str(int(totaldaysinspace[:d_index])+previousdays)+" days in space"
                    crewmemberpicture[isscrew] = str(data['people'][num-1]['biophoto'])
                    crewmembercountry[isscrew] = str(data['people'][num-1]['country']).title()
                    if(str(data['people'][num-1]['country'])==str('usa')):
                        crewmembercountry[isscrew] = str('USA')
                    isscrew = isscrew+1

            self.crew_screen.ids.crew1.text = str(crewmember[0])
            self.crew_screen.ids.crew1title.text = str(crewmembertitle[0])
            self.crew_screen.ids.crew1country.text = str(crewmembercountry[0])
            self.crew_screen.ids.crew1daysonISS.text = str(crewmemberdays[0])
            #self.crew_screen.ids.crew1image.source = str(crewmemberpicture[0])
            self.crew_screen.ids.crew2.text = str(crewmember[1])
            self.crew_screen.ids.crew2title.text = str(crewmembertitle[1])
            self.crew_screen.ids.crew2country.text = str(crewmembercountry[1])
            self.crew_screen.ids.crew2daysonISS.text = str(crewmemberdays[1])
            #self.crew_screen.ids.crew2image.source = str(crewmemberpicture[1])
            self.crew_screen.ids.crew3.text = str(crewmember[2])
            self.crew_screen.ids.crew3title.text = str(crewmembertitle[2])
            self.crew_screen.ids.crew3country.text = str(crewmembercountry[2])
            self.crew_screen.ids.crew3daysonISS.text = str(crewmemberdays[2])
            #self.crew_screen.ids.crew3image.source = str(crewmemberpicture[2])
            self.crew_screen.ids.crew4.text = str(crewmember[3])
            self.crew_screen.ids.crew4title.text = str(crewmembertitle[3])
            self.crew_screen.ids.crew4country.text = str(crewmembercountry[3])
            self.crew_screen.ids.crew4daysonISS.text = str(crewmemberdays[3])
            #self.crew_screen.ids.crew4image.source = str(crewmemberpicture[3])
            self.crew_screen.ids.crew5.text = str(crewmember[4])
            self.crew_screen.ids.crew5title.text = str(crewmembertitle[4])
            self.crew_screen.ids.crew5country.text = str(crewmembercountry[4])
            self.crew_screen.ids.crew5daysonISS.text = str(crewmemberdays[4])
            #self.crew_screen.ids.crew5image.source = str(crewmemberpicture[4])
            self.crew_screen.ids.crew6.text = str(crewmember[5])
            self.crew_screen.ids.crew6title.text = str(crewmembertitle[5])
            self.crew_screen.ids.crew6country.text = str(crewmembercountry[5])
            self.crew_screen.ids.crew6daysonISS.text = str(crewmemberdays[5])
            #self.crew_screen.ids.crew6image.source = str(crewmemberpicture[5])
            #self.crew_screen.ids.crew7.text = str(crewmember[6])
            #self.crew_screen.ids.crew7title.text = str(crewmembertitle[6])
            #self.crew_screen.ids.crew7country.text = str(crewmembercountry[6])
            #self.crew_screen.ids.crew7daysonISS.text = str(crewmemberdays[6])
            #self.crew_screen.ids.crew7image.source = str(crewmemberpicture[6])
            #self.crew_screen.ids.crew8.text = str(crewmember[7])
            #self.crew_screen.ids.crew8title.text = str(crewmembertitle[7])
            #self.crew_screen.ids.crew8country.text = str(crewmembercountry[7])
            #self.crew_screen.ids.crew8daysonISS.text = str(crewmemberdays[7])
            #self.crew_screen.ids.crew8image.source = str(crewmemberpicture[7]))
            #self.crew_screen.ids.crew9.text = str(crewmember[8])
            #self.crew_screen.ids.crew9title.text = str(crewmembertitle[8])
            #self.crew_screen.ids.crew9country.text = str(crewmembercountry[8])
            #self.crew_screen.ids.crew9daysonISS.text = str(crewmemberdays[8])
            #self.crew_screen.ids.crew9image.source = str(crewmemberpicture[8])
            #self.crew_screen.ids.crew10.text = str(crewmember[9])
            #self.crew_screen.ids.crew10title.text = str(crewmembertitle[9])
            #self.crew_screen.ids.crew10country.text = str(crewmembercountry[9])
            #self.crew_screen.ids.crew10daysonISS.text = str(crewmemberdays[9])
            #self.crew_screen.ids.crew10image.source = str(crewmemberpicture[9])
            #self.crew_screen.ids.crew11.text = str(crewmember[10])
            #self.crew_screen.ids.crew11title.text = str(crewmembertitle[10])
            #self.crew_screen.ids.crew11country.text = str(crewmembercountry[10])
            #self.crew_screen.ids.crew11daysonISS.text = str(crewmemberdays[10])
            #self.crew_screen.ids.crew11image.source = str(crewmemberpicture[10])
            #self.crew_screen.ids.crew12.text = str(crewmember[11])
            #self.crew_screen.ids.crew12title.text = str(crewmembertitle[11])
            #self.crew_screen.ids.crew12country.text = str(crewmembercountry[11])
            #self.crew_screen.ids.crew12daysonISS.text = str(crewmemberdays[11])
            #self.crew_screen.ids.crew12image.source = str(crewmemberpicture[11])

        def on_redirect(req, result):
            logWrite("Warning - checkCrew JSON failure (redirect)")

        def on_failure(req, result):
            logWrite("Warning - checkCrew JSON failure (url failure)")

        def on_error(req, result):
            logWrite("Warning - checkCrew JSON failure (url error)")
        
        req = UrlRequest(iss_crew_url, on_success, on_redirect, on_failure, on_error, timeout=1)

    def map_rotation(self, args):
        scalefactor = 0.083333
        scaledValue = float(args)/scalefactor
        return scaledValue

    def map_psi_bar(self, args):
        scalefactor = 0.015
        scaledValue = (float(args)*scalefactor)+0.72
        return scaledValue

    def map_hold_bar(self, args):
        scalefactor = 0.0015
        scaledValue = (float(args)*scalefactor)+0.71
        return scaledValue

    def hold_timer(self, dt):
        global seconds2, holdstartTime
        logWrite("Function Call - hold timer")
        unixconvert = time.gmtime(time.time())
        currenthours = float(unixconvert[7])*24+unixconvert[3]+float(unixconvert[4])/60+float(unixconvert[5])/3600
        seconds2 = (currenthours-EVAstartTime)*3600
        seconds2 = int(seconds2)

        new_bar_x = self.map_hold_bar(260-seconds2)
        self.us_eva.ids.leak_timer.text = "~"+ str(int(seconds2)) + "s"
        self.us_eva.ids.Hold_bar.pos_hint = {"center_x": new_bar_x, "center_y": 0.49}
        self.us_eva.ids.Crewlock_Status_image.source = '/home/pi/Mimic/Pi/imgs/eva/LeakCheckLights.png'

    def signal_unsubscribed(self): #change images, used stale signal image
        global internet, ScreenList

        if internet == False:
            for x in ScreenList:
                getattr(self, x).ids.signal.source = '/home/pi/Mimic/Pi/imgs/signal/offline.png'
            self.changeColors(1, 0, 0)
        else:
            for x in ScreenList:
                getattr(self, x).ids.signal.source = '/home/pi/Mimic/Pi/imgs/signal/SignalClientLost.png'
            self.changeColors(1, 0.5, 0)

        for x in ScreenList:
            getattr(self, x).ids.signal.size_hint_y = 0.112

    def signal_lost(self):
        global internet, ScreenList

        if internet == False:
            for x in ScreenList:
                getattr(self, x).ids.signal.source = '/home/pi/Mimic/Pi/imgs/signal/offline.png'
            self.changeColors(1, 0, 0)
        else:
            for x in ScreenList:
                getattr(self, x).ids.signal.source = '/home/pi/Mimic/Pi/imgs/signal/signalred.zip'
            self.changeColors(1, 0, 0)

        for x in ScreenList:
            getattr(self, x).ids.signal.anim_delay = 0.4
        for x in ScreenList:
            getattr(self, x).ids.signal.size_hint_y = 0.112

    def signal_acquired(self):
        global internet, ScreenList

        if internet == False:
            for x in ScreenList:
                getattr(self, x).ids.signal.source = '/home/pi/Mimic/Pi/imgs/signal/offline.png'
            self.changeColors(1, 0, 0)
        else:
            for x in ScreenList:
                getattr(self, x).ids.signal.source = '/home/pi/Mimic/Pi/imgs/signal/pulse-transparent.zip'
            self.changeColors(0, 1, 0)

        for x in ScreenList:
            getattr(self, x).ids.signal.anim_delay = 0.05
        for x in ScreenList:
            getattr(self, x).ids.signal.size_hint_y = 0.15

    def signal_stale(self):
        global internet, ScreenList

        if internet == False:
            for x in ScreenList:
                getattr(self, x).ids.signal.source = '/home/pi/Mimic/Pi/imgs/signal/offline.png'
            self.changeColors(1, 0, 0)
        else:
            for x in ScreenList:
                getattr(self, x).ids.signal.source = '/home/pi/Mimic/Pi/imgs/signal/SignalOrangeGray.png'
            self.changeColors(1, 0.5, 0)

        for x in ScreenList:
            getattr(self, x).ids.signal.anim_delay = 0.12
        for x in ScreenList:
            getattr(self, x).ids.signal.size_hint_y = 0.112

    def signal_client_offline(self):
        global internet, ScreenList

        if internet == False:
            for x in ScreenList:
                getattr(self, x).ids.signal.source = '/home/pi/Mimic/Pi/imgs/signal/offline.png'
            self.changeColors(1, 0, 0)
        else:
            for x in ScreenList:
                getattr(self, x).ids.signal.source = '/home/pi/Mimic/Pi/imgs/signal/SignalClientLost.png'
            self.changeColors(1, 0.5, 0)

        for x in ScreenList:
            getattr(self, x).ids.signal.anim_delay = 0.12
        for x in ScreenList:
            getattr(self, x).ids.signal.size_hint_y = 0.112

    def update_labels(self, dt):
        global mimicbutton, switchtofake, demoboolean, runningDemo, fakeorbitboolean, psarj2, ssarj2, manualcontrol, aos, los, oldLOS, psarjmc, ssarjmc, ptrrjmc, strrjmc, beta1bmc, beta1amc, beta2bmc, beta2amc, beta3bmc, beta3amc, beta4bmc, beta4amc, US_EVAinProgress, position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, altitude, velocity, iss_mass, testvalue, testfactor, airlock_pump, crewlockpres, leak_hold, firstcrossing, EVA_activities, repress, depress, oldAirlockPump, obtained_EVA_crew, EVAstartTime
        global holdstartTime, LS_Subscription, SerialConnection1, SerialConnection2, SerialConnection3, SerialConnection4, SerialConnection5
        global eva, standby, prebreath1, prebreath2, depress1, depress2, leakhold, repress
        global EPSstorageindex, channel1A_voltage, channel1B_voltage, channel2A_voltage, channel2B_voltage, channel3A_voltage, channel3B_voltage, channel4A_voltage, channel4B_voltage, USOS_Power
        global stationmode, sgant_elevation, sgant_xelevation
        global tdrs, module

        arduino_count = 0
        if SerialConnection1:
            arduino_count+=1
        if SerialConnection2:
            arduino_count+=1
        if SerialConnection3:
            arduino_count+=1
        if SerialConnection4:
            arduino_count+=1
        if SerialConnection5:
            arduino_count+=1

        if arduino_count > 0:
            self.mimic_screen.ids.arduino_count.text = str(arduino_count)
            self.mimic_screen.ids.arduino.source = "/home/pi/Mimic/Pi/imgs/signal/arduino_notransmit.png"
            self.fakeorbit_screen.ids.arduino.source = "/home/pi/Mimic/Pi/imgs/signal/arduino_notransmit.png"
            self.fakeorbit_screen.ids.arduino_count.text = str(arduino_count)
        else:
            self.mimic_screen.ids.arduino_count.text = ""
            self.fakeorbit_screen.ids.arduino_count.text = ""
            self.mimic_screen.ids.arduino.source = "/home/pi/Mimic/Pi/imgs/signal/arduino_offline.png"
            self.fakeorbit_screen.ids.arduino.source = "/home/pi/Mimic/Pi/imgs/signal/arduino_offline.png"
            runningDemo = False

        if SerialConnection1 or SerialConnection2 or SerialConnection3 or SerialConnection4 or SerialConnection5:
            self.mimic_screen.ids.mimicstartbutton.disabled = False
            self.fakeorbit_screen.ids.DemoStart.disabled = False
            self.fakeorbit_screen.ids.HTVDemoStart.disabled = False
            self.control_screen.ids.set90.disabled = False
            self.control_screen.ids.set0.disabled = False
            if mimicbutton:
                self.mimic_screen.ids.mimicstartbutton.disabled = True
                self.mimic_screen.ids.arduino.source = "/home/pi/Mimic/Pi/imgs/signal/Arduino_Transmit.zip"
            else:
                self.mimic_screen.ids.mimicstartbutton.disabled = False
        else:
            self.mimic_screen.ids.mimicstartbutton.disabled = True
            self.mimic_screen.ids.mimicstartbutton.text = "Transmit"
            self.fakeorbit_screen.ids.DemoStart.disabled = True
            self.fakeorbit_screen.ids.HTVDemoStart.disabled = True
            self.control_screen.ids.set90.disabled = True
            self.control_screen.ids.set0.disabled = True

        if runningDemo:
            self.fakeorbit_screen.ids.DemoStart.disabled = True
            self.fakeorbit_screen.ids.HTVDemoStart.disabled = True
            self.fakeorbit_screen.ids.DemoStop.disabled = False
            self.fakeorbit_screen.ids.HTVDemoStop.disabled = False
            self.fakeorbit_screen.ids.arduino.source = "/home/pi/Mimic/Pi/imgs/signal/Arduino_Transmit.zip"

        c.execute('select Value from telemetry')
        values = c.fetchall()
        c.execute('select Timestamp from telemetry')
        timestamps = c.fetchall()

        sub_status = str((values[255])[0]) #lightstreamer subscript checker
        client_status = str((values[256])[0]) #lightstreamer client checker
        
        psarj = "{:.2f}".format(float((values[0])[0]))
        if not switchtofake:
            psarj2 = float(psarj)
        if not manualcontrol:
            psarjmc = float(psarj)
        ssarj = "{:.2f}".format(float((values[1])[0]))
        if not switchtofake:
            ssarj2 = float(ssarj)
        if not manualcontrol:
            ssarjmc = float(ssarj)
        ptrrj = "{:.2f}".format(float((values[2])[0]))
        if not manualcontrol:
            ptrrjmc = float(ptrrj)
        strrj = "{:.2f}".format(float((values[3])[0]))
        if not manualcontrol:
            strrjmc = float(strrj)
        beta1b = "{:.2f}".format(float((values[4])[0]))
        if not switchtofake:
            beta1b2 = float(beta1b)
        if not manualcontrol:
            beta1bmc = float(beta1b)
        beta1a = "{:.2f}".format(float((values[5])[0]))
        if not switchtofake:
            beta1a2 = float(beta1a)
        if not manualcontrol:
            beta1amc = float(beta1a)
        beta2b = "{:.2f}".format(float((values[6])[0]))
        if not switchtofake:
            beta2b2 = float(beta2b) #+ 20.00
        if not manualcontrol:
            beta2bmc = float(beta2b)
        beta2a = "{:.2f}".format(float((values[7])[0]))
        if not switchtofake:
            beta2a2 = float(beta2a)
        if not manualcontrol:
            beta2amc = float(beta2a)
        beta3b = "{:.2f}".format(float((values[8])[0]))
        if not switchtofake:
            beta3b2 = float(beta3b)
        if not manualcontrol:
            beta3bmc = float(beta3b)
        beta3a = "{:.2f}".format(float((values[9])[0]))
        if not switchtofake:
            beta3a2 = float(beta3a)
        if not manualcontrol:
            beta3amc = float(beta3a)
        beta4b = "{:.2f}".format(float((values[10])[0]))
        if not switchtofake:
            beta4b2 = float(beta4b)
        if not manualcontrol:
            beta4bmc = float(beta4b)
        beta4a = "{:.2f}".format(float((values[11])[0]))
        if not switchtofake:
            beta4a2 = float(beta4a) #+ 20.00
        if not manualcontrol:
            beta4amc = float(beta4a)

        aos = "{:.2f}".format(int((values[12])[0]))
        los = "{:.2f}".format(int((values[13])[0]))
        sasa_el = "{:.2f}".format(float((values[14])[0]))
        active_sasa = int((values[54])[0])
        sasa1_active = int((values[53])[0])
        sasa2_active = int((values[52])[0])
        sgant_elevation = float((values[15])[0])
        sgant_xelevation = float((values[17])[0])
        sgant_transmit = float((values[41])[0])
        uhf1_power = int((values[233])[0]) #0 = off, 1 = on, 3 = failed
        uhf2_power = int((values[234])[0]) #0 = off, 1 = on, 3 = failed
        uhf_framesync = int((values[235])[0]) #1 or 0

        v1a = "{:.2f}".format(float((values[25])[0]))
        channel1A_voltage[EPSstorageindex] = float(v1a)
        v1b = "{:.2f}".format(float((values[26])[0]))
        channel1B_voltage[EPSstorageindex] = float(v1b)
        v2a = "{:.2f}".format(float((values[27])[0]))
        channel2A_voltage[EPSstorageindex] = float(v2a)
        v2b = "{:.2f}".format(float((values[28])[0]))
        channel2B_voltage[EPSstorageindex] = float(v2b)
        v3a = "{:.2f}".format(float((values[29])[0]))
        channel3A_voltage[EPSstorageindex] = float(v3a)
        v3b = "{:.2f}".format(float((values[30])[0]))
        channel3B_voltage[EPSstorageindex] = float(v3b)
        v4a = "{:.2f}".format(float((values[31])[0]))
        channel4A_voltage[EPSstorageindex] = float(v4a)
        v4b = "{:.2f}".format(float((values[32])[0]))
        channel4B_voltage[EPSstorageindex] = float(v4b)
        c1a = "{:.2f}".format(float((values[33])[0]))
        c1b = "{:.2f}".format(float((values[34])[0]))
        c2a = "{:.2f}".format(float((values[35])[0]))
        c2b = "{:.2f}".format(float((values[36])[0]))
        c3a = "{:.2f}".format(float((values[37])[0]))
        c3b = "{:.2f}".format(float((values[38])[0]))
        c4a = "{:.2f}".format(float((values[39])[0]))
        c4b = "{:.2f}".format(float((values[40])[0]))

        stationmode = float((values[46])[0]) #russian segment mode same as usos mode

        #GNC Telemetry
        rollerror = float((values[165])[0])
        pitcherror = float((values[166])[0])
        yawerror = float((values[167])[0])

        quaternion0 = float((values[171])[0])
        quaternion1 = float((values[172])[0])
        quaternion2 = float((values[173])[0])
        quaternion3 = float((values[174])[0])

        iss_mass = "{:.2f}".format(float((values[48])[0]))
        position_x = "{:.2f}".format(float((values[55])[0]))
        position_y = "{:.2f}".format(float((values[56])[0]))
        position_z = "{:.2f}".format(float((values[57])[0]))
        velocity_x = "{:.2f}".format(float((values[58])[0]))
        velocity_y = "{:.2f}".format(float((values[59])[0]))
        velocity_z = "{:.2f}".format(float((values[60])[0]))

        altitude = "{:.2f}".format((math.sqrt( math.pow(float(position_x), 2) + math.pow(float(position_y), 2) + math.pow(float(position_z), 2) )-6371.00))
        velocity = "{:.2f}".format(((math.sqrt( math.pow(float(velocity_x), 2) + math.pow(float(velocity_y), 2) + math.pow(float(velocity_z), 2) ))/1.00))

        cmg1_active = int((values[145])[0])
        cmg2_active = int((values[146])[0])
        cmg3_active = int((values[147])[0])
        cmg4_active = int((values[148])[0])
        numCMGs = int((values[149])[0])
        CMGtorqueRoll = float((values[150])[0])
        CMGtorquePitch = float((values[151])[0])
        CMGtorqueYaw = float((values[152])[0])
        CMGmomentum = float((values[153])[0])
        CMGmompercent = float((values[154])[0])
        CMGmomcapacity = float((values[175])[0])
        cmg1_spintemp = float((values[181])[0])
        cmg2_spintemp = float((values[182])[0])
        cmg3_spintemp = float((values[183])[0])
        cmg4_spintemp = float((values[184])[0])
        cmg1_halltemp = float((values[185])[0])
        cmg2_halltemp = float((values[186])[0])
        cmg3_halltemp = float((values[187])[0])
        cmg4_halltemp = float((values[188])[0])
        cmg1_vibration = float((values[237])[0])
        cmg2_vibration = float((values[238])[0])
        cmg3_vibration = float((values[239])[0])
        cmg4_vibration = float((values[240])[0])
        cmg1_motorcurrent = float((values[241])[0])
        cmg2_motorcurrent = float((values[242])[0])
        cmg3_motorcurrent = float((values[243])[0])
        cmg4_motorcurrent = float((values[244])[0])
        cmg1_wheelspeed = float((values[245])[0])
        cmg2_wheelspeed = float((values[246])[0])
        cmg3_wheelspeed = float((values[247])[0])
        cmg4_wheelspeed = float((values[248])[0])

        #EVA Telemetry
        airlock_pump_voltage = int((values[71])[0])
        airlock_pump_voltage_timestamp = float((timestamps[71])[0])
        airlock_pump_switch = int((values[72])[0])
        crewlockpres = float((values[16])[0])
        airlockpres = float((values[77])[0])


        ##US EPS Stuff---------------------------##

        solarbeta = "{:.2f}".format(float((values[176])[0]))

        power_1a = float(v1a) * float(c1a)
        power_1b = float(v1b) * float(c1b)
        power_2a = float(v2a) * float(c2a)
        power_2b = float(v2b) * float(c2b)
        power_3a = float(v3a) * float(c3a)
        power_3b = float(v3b) * float(c3b)
        power_4a = float(v4a) * float(c4a)
        power_4b = float(v4b) * float(c4b)

        USOS_Power = power_1a + power_1b + power_2a + power_2b + power_3a + power_3b + power_4a + power_4b
        self.eps_screen.ids.usos_power.text = str("{:.0f}".format(USOS_Power*-1.0)) + " W"
        self.eps_screen.ids.solarbeta.text = str(solarbeta)

        avg_total_voltage = (float(v1a)+float(v1b)+float(v2a)+float(v2b)+float(v3a)+float(v3b)+float(v4a)+float(v4b))/8.0

        avg_1a = (channel1A_voltage[0]+channel1A_voltage[1]+channel1A_voltage[2]+channel1A_voltage[3]+channel1A_voltage[4]+channel1A_voltage[5]+channel1A_voltage[6]+channel1A_voltage[7]+channel1A_voltage[8]+channel1A_voltage[9])/10
        avg_1b = (channel1B_voltage[0]+channel1B_voltage[1]+channel1B_voltage[2]+channel1B_voltage[3]+channel1B_voltage[4]+channel1B_voltage[5]+channel1B_voltage[6]+channel1B_voltage[7]+channel1B_voltage[8]+channel1B_voltage[9])/10
        avg_2a = (channel2A_voltage[0]+channel2A_voltage[1]+channel2A_voltage[2]+channel2A_voltage[3]+channel2A_voltage[4]+channel2A_voltage[5]+channel2A_voltage[6]+channel2A_voltage[7]+channel2A_voltage[8]+channel2A_voltage[9])/10
        avg_2b = (channel2B_voltage[0]+channel2B_voltage[1]+channel2B_voltage[2]+channel2B_voltage[3]+channel2B_voltage[4]+channel2B_voltage[5]+channel2B_voltage[6]+channel2B_voltage[7]+channel2B_voltage[8]+channel2B_voltage[9])/10
        avg_3a = (channel3A_voltage[0]+channel3A_voltage[1]+channel3A_voltage[2]+channel3A_voltage[3]+channel3A_voltage[4]+channel3A_voltage[5]+channel3A_voltage[6]+channel3A_voltage[7]+channel3A_voltage[8]+channel3A_voltage[9])/10
        avg_3b = (channel3B_voltage[0]+channel3B_voltage[1]+channel3B_voltage[2]+channel3B_voltage[3]+channel3B_voltage[4]+channel3B_voltage[5]+channel3B_voltage[6]+channel3B_voltage[7]+channel3B_voltage[8]+channel3B_voltage[9])/10
        avg_4a = (channel4A_voltage[0]+channel4A_voltage[1]+channel4A_voltage[2]+channel4A_voltage[3]+channel4A_voltage[4]+channel4A_voltage[5]+channel4A_voltage[6]+channel4A_voltage[7]+channel4A_voltage[8]+channel4A_voltage[9])/10
        avg_4b = (channel4B_voltage[0]+channel4B_voltage[1]+channel4B_voltage[2]+channel4B_voltage[3]+channel4B_voltage[4]+channel4B_voltage[5]+channel4B_voltage[6]+channel4B_voltage[7]+channel4B_voltage[8]+channel4B_voltage[9])/10
        halfavg_1a = (channel1A_voltage[0]+channel1A_voltage[1]+channel1A_voltage[2]+channel1A_voltage[3]+channel1A_voltage[4])/5
        halfavg_1b = (channel1B_voltage[0]+channel1B_voltage[1]+channel1B_voltage[2]+channel1B_voltage[3]+channel1B_voltage[4])/5
        halfavg_2a = (channel2A_voltage[0]+channel2A_voltage[1]+channel2A_voltage[2]+channel2A_voltage[3]+channel2A_voltage[4])/5
        halfavg_2b = (channel2B_voltage[0]+channel2B_voltage[1]+channel2B_voltage[2]+channel2B_voltage[3]+channel2B_voltage[4])/5
        halfavg_3a = (channel3A_voltage[0]+channel3A_voltage[1]+channel3A_voltage[2]+channel3A_voltage[3]+channel3A_voltage[4])/5
        halfavg_3b = (channel3B_voltage[0]+channel3B_voltage[1]+channel3B_voltage[2]+channel3B_voltage[3]+channel3B_voltage[4])/5
        halfavg_4a = (channel4A_voltage[0]+channel4A_voltage[1]+channel4A_voltage[2]+channel4A_voltage[3]+channel4A_voltage[4])/5
        halfavg_4b = (channel4B_voltage[0]+channel4B_voltage[1]+channel4B_voltage[2]+channel4B_voltage[3]+channel4B_voltage[4])/5

        EPSstorageindex += 1
        if EPSstorageindex > 9:
            EPSstorageindex = 0


        ## Station Mode ##

        if stationmode == 1.0:
            self.iss_screen.ids.stationmode_value.text = "Crew Rescue"
        elif stationmode == 2.0:
            self.iss_screen.ids.stationmode_value.text = "Survival"
        elif stationmode == 3.0:
            self.iss_screen.ids.stationmode_value.text = "Reboost"
        elif stationmode == 4.0:
            self.iss_screen.ids.stationmode_value.text = "Proximity Operations"
        elif stationmode == 5.0:
            self.iss_screen.ids.stationmode_value.text = "EVA"
        elif stationmode == 6.0:
            self.iss_screen.ids.stationmode_value.text = "Microgravity"
        elif stationmode == 7.0:
            self.iss_screen.ids.stationmode_value.text = "Standard"
        else:
            self.iss_screen.ids.stationmode_value.text = "n/a"

        ## ISS Potential Problems ##
        #ISS Leak - Check Pressure Levels
        #Number of CMGs online could reveal CMG failure
        #CMG speed less than 6600rpm
        #Solar arrays offline
        #Loss of attitude control, loss of cmg control
        #ISS altitude too low
        #Russion hook status - make sure all modules remain docked


        ##-------------------GNC Stuff---------------------------##

        roll = math.degrees(math.atan2(2.0 * (quaternion0 * quaternion1 + quaternion2 * quaternion3), 1.0 - 2.0 * (quaternion1 * quaternion1 + quaternion2 * quaternion2))) + rollerror
        pitch = math.degrees(math.asin(max(-1.0, min(1.0, 2.0 * (quaternion0 * quaternion2 - quaternion3 * quaternion1))))) + pitcherror
        yaw = math.degrees(math.atan2(2.0 * (quaternion0 * quaternion3 + quaternion1 * quaternion2), 1.0 - 2.0 * (quaternion2 * quaternion2 + quaternion3 * quaternion3))) + yawerror

        self.gnc_screen.ids.yaw.text = str("{:.2f}".format(yaw))
        self.gnc_screen.ids.pitch.text = str("{:.2f}".format(pitch))
        self.gnc_screen.ids.roll.text = str("{:.2f}".format(roll))

        self.gnc_screen.ids.cmgsaturation.value = CMGmompercent
        self.gnc_screen.ids.cmgsaturation_value.text = "CMG Saturation " + str("{:.1f}".format(CMGmompercent)) + "%"

        if cmg1_active == 1:
            self.gnc_screen.ids.cmg1.source = "/home/pi/Mimic/Pi/imgs/gnc/cmg.png"
        else:
            self.gnc_screen.ids.cmg1.source = "/home/pi/Mimic/Pi/imgs/gnc/cmg_offline.png"

        if cmg2_active == 1:
            self.gnc_screen.ids.cmg2.source = "/home/pi/Mimic/Pi/imgs/gnc/cmg.png"
        else:
            self.gnc_screen.ids.cmg2.source = "/home/pi/Mimic/Pi/imgs/gnc/cmg_offline.png"

        if cmg3_active == 1:
            self.gnc_screen.ids.cmg3.source = "/home/pi/Mimic/Pi/imgs/gnc/cmg.png"
        else:
            self.gnc_screen.ids.cmg3.source = "/home/pi/Mimic/Pi/imgs/gnc/cmg_offline.png"

        if cmg4_active == 1:
            self.gnc_screen.ids.cmg4.source = "/home/pi/Mimic/Pi/imgs/gnc/cmg.png"
        else:
            self.gnc_screen.ids.cmg4.source = "/home/pi/Mimic/Pi/imgs/gnc/cmg_offline.png"

        self.gnc_screen.ids.cmg1spintemp.text = "Spin Temp " + str("{:.1f}".format(cmg1_spintemp))
        self.gnc_screen.ids.cmg1halltemp.text = "Hall Temp " + str("{:.1f}".format(cmg1_halltemp))
        self.gnc_screen.ids.cmg1vibration.text = "Vibration " + str("{:.4f}".format(cmg1_vibration))
        self.gnc_screen.ids.cmg1current.text = "Current " + str("{:.1f}".format(cmg1_motorcurrent))
        self.gnc_screen.ids.cmg1speed.text = "Speed " + str("{:.1f}".format(cmg1_wheelspeed))

        self.gnc_screen.ids.cmg2spintemp.text = "Spin Temp " + str("{:.1f}".format(cmg2_spintemp))
        self.gnc_screen.ids.cmg2halltemp.text = "Hall Temp " + str("{:.1f}".format(cmg2_halltemp))
        self.gnc_screen.ids.cmg2vibration.text = "Vibration " + str("{:.4f}".format(cmg2_vibration))
        self.gnc_screen.ids.cmg2current.text = "Current " + str("{:.1f}".format(cmg2_motorcurrent))
        self.gnc_screen.ids.cmg2speed.text = "Speed " + str("{:.1f}".format(cmg2_wheelspeed))

        self.gnc_screen.ids.cmg3spintemp.text = "Spin Temp " + str("{:.1f}".format(cmg3_spintemp))
        self.gnc_screen.ids.cmg3halltemp.text = "Hall Temp " + str("{:.1f}".format(cmg3_halltemp))
        self.gnc_screen.ids.cmg3vibration.text = "Vibration " + str("{:.4f}".format(cmg3_vibration))
        self.gnc_screen.ids.cmg3current.text = "Current " + str("{:.1f}".format(cmg3_motorcurrent))
        self.gnc_screen.ids.cmg3speed.text = "Speed " + str("{:.1f}".format(cmg3_wheelspeed))

        self.gnc_screen.ids.cmg4spintemp.text = "Spin Temp " + str("{:.1f}".format(cmg4_spintemp))
        self.gnc_screen.ids.cmg4halltemp.text = "Hall Temp " + str("{:.1f}".format(cmg4_halltemp))
        self.gnc_screen.ids.cmg4vibration.text = "Vibration " + str("{:.4f}".format(cmg4_vibration))
        self.gnc_screen.ids.cmg4current.text = "Current " + str("{:.1f}".format(cmg4_motorcurrent))
        self.gnc_screen.ids.cmg4speed.text = "Speed " + str("{:.1f}".format(cmg4_wheelspeed))

        ##-------------------EPS Stuff---------------------------##

        if avg_total_voltage > 151.5:
            self.eps_screen.ids.eps_sun.color = 1, 1, 1, 1
        else:
            self.eps_screen.ids.eps_sun.color = 1, 1, 1, 0.1

        if halfavg_1a < 151.5: #discharging
            self.eps_screen.ids.array_1a.source = "/home/pi/Mimic/Pi/imgs/eps/array-discharging.zip"
            #self.eps_screen.ids.array_1a.color = 1, 1, 1, 0.8
        elif avg_1a > 160.0: #charged
            self.eps_screen.ids.array_1a.source = "/home/pi/Mimic/Pi/imgs/eps/array-charged.zip"
        elif halfavg_1a >= 151.5:  #charging
            self.eps_screen.ids.array_1a.source = "/home/pi/Mimic/Pi/imgs/eps/array-charging.zip"
            self.eps_screen.ids.array_1a.color = 1, 1, 1, 1.0
        if float(c1a) > 0.0:    #power channel offline!
            self.eps_screen.ids.array_1a.source = "/home/pi/Mimic/Pi/imgs/eps/array-offline.png"

        if halfavg_1b < 151.5: #discharging
            self.eps_screen.ids.array_1b.source = "/home/pi/Mimic/Pi/imgs/eps/array-discharging.zip"
            #self.eps_screen.ids.array_1b.color = 1, 1, 1, 0.8
        elif avg_1b > 160.0: #charged
            self.eps_screen.ids.array_1b.source = "/home/pi/Mimic/Pi/imgs/eps/array-charged.zip"
        elif halfavg_1b >= 151.5:  #charging
            self.eps_screen.ids.array_1b.source = "/home/pi/Mimic/Pi/imgs/eps/array-charging.zip"
            self.eps_screen.ids.array_1b.color = 1, 1, 1, 1.0
        if float(c1b) > 0.0:                                  #power channel offline!
            self.eps_screen.ids.array_1b.source = "/home/pi/Mimic/Pi/imgs/eps/array-offline.png"

        if halfavg_2a < 151.5: #discharging
            self.eps_screen.ids.array_2a.source = "/home/pi/Mimic/Pi/imgs/eps/array-discharging.zip"
            #self.eps_screen.ids.array_2a.color = 1, 1, 1, 0.8
        elif avg_2a > 160.0: #charged
            self.eps_screen.ids.array_2a.source = "/home/pi/Mimic/Pi/imgs/eps/array-charged.zip"
        elif halfavg_2a >= 151.5:  #charging
            self.eps_screen.ids.array_2a.source = "/home/pi/Mimic/Pi/imgs/eps/array-charging.zip"
            self.eps_screen.ids.array_2a.color = 1, 1, 1, 1.0
        if float(c2a) > 0.0:                                  #power channel offline!
            self.eps_screen.ids.array_2a.source = "/home/pi/Mimic/Pi/imgs/eps/array-offline.png"

        if halfavg_2b < 151.5: #discharging
            self.eps_screen.ids.array_2b.source = "/home/pi/Mimic/Pi/imgs/eps/array-discharging.zip"
            #self.eps_screen.ids.array_2b.color = 1, 1, 1, 0.8
        elif avg_2b > 160.0: #charged
            self.eps_screen.ids.array_2b.source = "/home/pi/Mimic/Pi/imgs/eps/array-charged.zip"
        elif halfavg_2b >= 151.5:  #charging
            self.eps_screen.ids.array_2b.source = "/home/pi/Mimic/Pi/imgs/eps/array-charging.zip"
            self.eps_screen.ids.array_2b.color = 1, 1, 1, 1.0
        if float(c2b) > 0.0:                                  #power channel offline!
            self.eps_screen.ids.array_2b.source = "/home/pi/Mimic/Pi/imgs/eps/array-offline.png"

        if halfavg_3a < 151.5: #discharging
            self.eps_screen.ids.array_3a.source = "/home/pi/Mimic/Pi/imgs/eps/array-discharging.zip"
            #self.eps_screen.ids.array_3a.color = 1, 1, 1, 0.8
        elif avg_3a > 160.0: #charged
            self.eps_screen.ids.array_3a.source = "/home/pi/Mimic/Pi/imgs/eps/array-charged.zip"
        elif halfavg_3a >= 151.5:  #charging
            self.eps_screen.ids.array_3a.source = "/home/pi/Mimic/Pi/imgs/eps/array-charging.zip"
            self.eps_screen.ids.array_3a.color = 1, 1, 1, 1.0
        if float(c3a) > 0.0:                                  #power channel offline!
            self.eps_screen.ids.array_3a.source = "/home/pi/Mimic/Pi/imgs/eps/array-offline.png"

        if halfavg_3b < 151.5: #discharging
            self.eps_screen.ids.array_3b.source = "/home/pi/Mimic/Pi/imgs/eps/array-discharging.zip"
            #self.eps_screen.ids.array_3b.color = 1, 1, 1, 0.8
        elif avg_3b > 160.0: #charged
            self.eps_screen.ids.array_3b.source = "/home/pi/Mimic/Pi/imgs/eps/array-charged.zip"
        elif halfavg_3b >= 151.5:  #charging
            self.eps_screen.ids.array_3b.source = "/home/pi/Mimic/Pi/imgs/eps/array-charging.zip"
            self.eps_screen.ids.array_3b.color = 1, 1, 1, 1.0
        if float(c3b) > 0.0:                                  #power channel offline!
            self.eps_screen.ids.array_3b.source = "/home/pi/Mimic/Pi/imgs/eps/array-offline.png"

        if halfavg_4a < 151.5: #discharging
            self.eps_screen.ids.array_4a.source = "/home/pi/Mimic/Pi/imgs/eps/array-discharging.zip"
            #self.eps_screen.ids.array_4a.color = 1, 1, 1, 0.8
        elif avg_4a > 160.0: #charged
            self.eps_screen.ids.array_4a.source = "/home/pi/Mimic/Pi/imgs/eps/array-charged.zip"
        elif halfavg_4a >= 151.5:  #charging
            self.eps_screen.ids.array_4a.source = "/home/pi/Mimic/Pi/imgs/eps/array-charging.zip"
            self.eps_screen.ids.array_4a.color = 1, 1, 1, 1.0
        if float(c4a) > 0.0:                                  #power channel offline!
            self.eps_screen.ids.array_4a.source = "/home/pi/Mimic/Pi/imgs/eps/array-offline.png"

        if halfavg_4b < 151.5: #discharging
            self.eps_screen.ids.array_4b.source = "/home/pi/Mimic/Pi/imgs/eps/array-discharging.zip"
            #self.eps_screen.ids.array_4b.color = 1, 1, 1, 0.8
        elif avg_4b > 160.0: #charged
            self.eps_screen.ids.array_4b.source = "/home/pi/Mimic/Pi/imgs/eps/array-charged.zip"
        elif halfavg_4b >= 151.5:  #charging
            self.eps_screen.ids.array_4b.source = "/home/pi/Mimic/Pi/imgs/eps/array-charging.zip"
            self.eps_screen.ids.array_4b.color = 1, 1, 1, 1.0
        if float(c4b) > 0.0:                                  #power channel offline!
            self.eps_screen.ids.array_4b.source = "/home/pi/Mimic/Pi/imgs/eps/array-offline.png"

        ##-------------------C&T Functionality-------------------##
        self.ct_sgant_screen.ids.sgant_dish.angle = float(sgant_elevation)
        self.ct_sgant_screen.ids.sgant_elevation.text = "{:.2f}".format(float(sgant_elevation))

        #make sure radio animations turn off when no signal or no transmit
        if float(sgant_transmit) == 1.0 and float(aos) == 1.0:
            self.ct_sgant_screen.ids.radio_up.color = 1, 1, 1, 1
            if tdrs == "west":
                self.ct_sgant_screen.ids.tdrs_west.source = "/home/pi/Mimic/Pi/imgs/ct/TDRS.zip"
                self.ct_sgant_screen.ids.tdrs_east.source = "/home/pi/Mimic/Pi/imgs/ct/TDRS.png"
                self.ct_sgant_screen.ids.tdrs_z.source = "/home/pi/Mimic/Pi/imgs/ct/TDRS.png"
            elif tdrs == "east":
                self.ct_sgant_screen.ids.tdrs_east.source = "/home/pi/Mimic/Pi/imgs/ct/TDRS.zip"
                self.ct_sgant_screen.ids.tdrs_west.source = "/home/pi/Mimic/Pi/imgs/ct/TDRS.png"
                self.ct_sgant_screen.ids.tdrs_z.source = "/home/pi/Mimic/Pi/imgs/ct/TDRS.png"
            elif tdrs == "z":
                self.ct_sgant_screen.ids.tdrs_z.source = "/home/pi/Mimic/Pi/imgs/ct/TDRS.zip"
                self.ct_sgant_screen.ids.tdrs_west.source = "/home/pi/Mimic/Pi/imgs/ct/TDRS.png"
                self.ct_sgant_screen.ids.tdrs_east.source = "/home/pi/Mimic/Pi/imgs/ct/TDRS.png"
        elif float(sgant_transmit) == 1.0 and float(aos) == 0.0:
            self.ct_sgant_screen.ids.radio_up.color = 0, 0, 0, 0
            self.ct_sgant_screen.ids.tdrs_east.source = "/home/pi/Mimic/Pi/imgs/ct/TDRS.png"
            self.ct_sgant_screen.ids.tdrs_west.source = "/home/pi/Mimic/Pi/imgs/ct/TDRS.png"
            self.ct_sgant_screen.ids.tdrs_z.source = "/home/pi/Mimic/Pi/imgs/ct/TDRS.png"
        elif float(sgant_transmit) == 0.0:
            self.ct_sgant_screen.ids.radio_up.color = 0, 0, 0, 0
            self.ct_sgant_screen.ids.tdrs_east.source = "/home/pi/Mimic/Pi/imgs/ct/TDRS.png"
            self.ct_sgant_screen.ids.tdrs_west.source = "/home/pi/Mimic/Pi/imgs/ct/TDRS.png"
            self.ct_sgant_screen.ids.tdrs_z.source = "/home/pi/Mimic/Pi/imgs/ct/TDRS.png"
        elif float(aos) == 0.0:
            self.ct_sgant_screen.ids.radio_up.color = 0, 0, 0, 0
            self.ct_sgant_screen.ids.tdrs_east.source = "/home/pi/Mimic/Pi/imgs/ct/TDRS.png"
            self.ct_sgant_screen.ids.tdrs_west.source = "/home/pi/Mimic/Pi/imgs/ct/TDRS.png"
            self.ct_sgant_screen.ids.tdrs_z.source = "/home/pi/Mimic/Pi/imgs/ct/TDRS.png"

        #now check main CT screen radio signal
        if float(sgant_transmit) == 1.0 and float(aos) == 1.0:
            self.ct_screen.ids.sgant1_radio.color = 1, 1, 1, 1
            self.ct_screen.ids.sgant2_radio.color = 1, 1, 1, 1
        elif float(sgant_transmit) == 1.0 and float(aos) == 0.0:
            self.ct_screen.ids.sgant1_radio.color = 0, 0, 0, 0
            self.ct_screen.ids.sgant2_radio.color = 0, 0, 0, 0
        elif float(sgant_transmit) == 0.0:
            self.ct_screen.ids.sgant1_radio.color = 0, 0, 0, 0
            self.ct_screen.ids.sgant2_radio.color = 0, 0, 0, 0
        elif float(aos) == 0.0:
            self.ct_screen.ids.sgant1_radio.color = 0, 0, 0, 0
            self.ct_screen.ids.sgant2_radio.color = 0, 0, 0, 0

        if float(sasa1_active) == 1.0 and float(aos) == 1.0:
            self.ct_screen.ids.sasa1_radio.color = 1, 1, 1, 1
        elif float(sasa1_active) == 1.0 and float(aos) == 0.0:
            self.ct_screen.ids.sasa1_radio.color = 0, 0, 0, 0
        elif float(sasa1_active) == 0.0:
            self.ct_screen.ids.sasa1_radio.color = 0, 0, 0, 0
        elif float(aos) == 0.0:
            self.ct_screen.ids.sasa1_radio.color = 0, 0, 0, 0


        if float(sasa2_active) == 1.0 and float(aos) == 1.0:
            self.ct_screen.ids.sasa2_radio.color = 1, 1, 1, 1
        elif float(sasa2_active) == 1.0 and float(aos) == 0.0:
            self.ct_screen.ids.sasa2_radio.color = 0, 0, 0, 0
        elif float(sasa2_active) == 0.0:
            self.ct_screen.ids.sasa2_radio.color = 0, 0, 0, 0
        elif float(aos) == 0.0:
            self.ct_screen.ids.sasa2_radio.color = 0, 0, 0, 0

        if float(uhf1_power) == 1.0 and float(aos) == 1.0:
            self.ct_screen.ids.uhf1_radio.color = 1, 1, 1, 1
        elif float(uhf1_power) == 1.0 and float(aos) == 0.0:
            self.ct_screen.ids.uhf1_radio.color = 1, 0, 0, 1
        elif float(uhf1_power) == 0.0:
            self.ct_screen.ids.uhf1_radio.color = 0, 0, 0, 0

        if float(uhf2_power) == 1.0 and float(aos) == 1.0:
            self.ct_screen.ids.uhf2_radio.color = 1, 1, 1, 1
        elif float(uhf2_power) == 1.0 and float(aos) == 0.0:
            self.ct_screen.ids.uhf2_radio.color = 1, 0, 0, 1
        elif float(uhf2_power) == 0.0:
            self.ct_screen.ids.uhf2_radio.color = 0, 0, 0, 0

        ##-------------------EVA Functionality-------------------##
        if stationmode == 5:
            evaflashevent = Clock.schedule_once(self.flashEVAbutton, 1)

        ##-------------------US EVA Functionality-------------------##


        if airlock_pump_voltage == 1:
            self.us_eva.ids.pumpvoltage.text = "Airlock Pump Power On!"
            self.us_eva.ids.pumpvoltage.color = 0.33, 0.7, 0.18
        else:
            self.us_eva.ids.pumpvoltage.text = "Airlock Pump Power Off"
            self.us_eva.ids.pumpvoltage.color = 0, 0, 0

        if airlock_pump_switch == 1:
            self.us_eva.ids.pumpswitch.text = "Airlock Pump Active!"
            self.us_eva.ids.pumpswitch.color = 0.33, 0.7, 0.18
        else:
            self.us_eva.ids.pumpswitch.text = "Airlock Pump Inactive"
            self.us_eva.ids.pumpswitch.color = 0, 0, 0

        ##activate EVA button flash
        if (airlock_pump_voltage == 1 or crewlockpres < 734) and int(stationmode) == 5:
            usevaflashevent = Clock.schedule_once(self.flashUS_EVAbutton, 1)

        ##No EVA Currently
        if airlock_pump_voltage == 0 and airlock_pump_switch == 0 and crewlockpres > 740 and airlockpres > 740:
            eva = False
            self.us_eva.ids.leak_timer.text = ""
            self.us_eva.ids.Crewlock_Status_image.source = '/home/pi/Mimic/Pi/imgs/eva/BlankLights.png'
            self.us_eva.ids.EVA_occuring.color = 1, 0, 0
            self.us_eva.ids.EVA_occuring.text = "Currently No EVA"

        ##EVA Standby - NOT UNIQUE
        if airlock_pump_voltage == 1 and airlock_pump_switch == 1 and crewlockpres > 740 and airlockpres > 740 and int(stationmode) == 5:
            standby = True
            self.us_eva.ids.leak_timer.text = "~160s Leak Check"
            self.us_eva.ids.Crewlock_Status_image.source = '/home/pi/Mimic/Pi/imgs/eva/StandbyLights.png'
            self.us_eva.ids.EVA_occuring.color = 0, 0, 1
            self.us_eva.ids.EVA_occuring.text = "EVA Standby"
        else:
            standby = False

        ##EVA Prebreath Pressure
        if airlock_pump_voltage == 1 and crewlockpres > 740 and airlockpres > 740 and int(stationmode) == 5:
            prebreath1 = True
            self.us_eva.ids.Crewlock_Status_image.source = '/home/pi/Mimic/Pi/imgs/eva/PreBreatheLights.png'
            self.us_eva.ids.leak_timer.text = "~160s Leak Check"
            self.us_eva.ids.EVA_occuring.color = 0, 0, 1
            self.us_eva.ids.EVA_occuring.text = "Pre-EVA Nitrogen Purge"

        ##EVA Depress1
        if airlock_pump_voltage == 1 and airlock_pump_switch == 1 and crewlockpres < 740 and airlockpres > 740 and int(stationmode) == 5:
            depress1 = True
            self.us_eva.ids.leak_timer.text = "~160s Leak Check"
            self.us_eva.ids.EVA_occuring.text = "Crewlock Depressurizing"
            self.us_eva.ids.EVA_occuring.color = 0, 0, 1
            self.us_eva.ids.Crewlock_Status_image.source = '/home/pi/Mimic/Pi/imgs/eva/DepressLights.png'

        ##EVA Leakcheck
        if airlock_pump_voltage == 1 and crewlockpres < 260 and crewlockpres > 250 and (depress1 or leakhold) and int(stationmode) == 5:
            if depress1:
                holdstartTime = float(unixconvert[7])*24+unixconvert[3]+float(unixconvert[4])/60+float(unixconvert[5])/3600
            leakhold = True
            depress1 = False
            self.us_eva.ids.EVA_occuring.text = "Leak Check in Progress!"
            self.us_eva.ids.EVA_occuring.color = 0, 0, 1
            Clock.schedule_once(self.hold_timer, 1)
            self.us_eva.ids.Crewlock_Status_image.source = '/home/pi/Mimic/Pi/imgs/eva/LeakCheckLights.png'
        else:
            leakhold = False

        ##EVA Depress2
        if airlock_pump_voltage == 1 and crewlockpres <= 250 and crewlockpres > 3 and int(stationmode) == 5:
            leakhold = False
            self.us_eva.ids.leak_timer.text = "Complete"
            self.us_eva.ids.EVA_occuring.text = "Crewlock Depressurizing"
            self.us_eva.ids.EVA_occuring.color = 0, 0, 1
            self.us_eva.ids.Crewlock_Status_image.source = '/home/pi/Mimic/Pi/imgs/eva/DepressLights.png'

        ##EVA in progress
        if crewlockpres < 2.5 and int(stationmode) == 5:
            eva = True
            self.us_eva.ids.EVA_occuring.text = "EVA In Progress!!!"
            self.us_eva.ids.EVA_occuring.color = 0.33, 0.7, 0.18
            self.us_eva.ids.leak_timer.text = "Complete"
            self.us_eva.ids.Crewlock_Status_image.source = '/home/pi/Mimic/Pi/imgs/eva/InProgressLights.png'
            evatimerevent = Clock.schedule_once(self.EVA_clock, 1)

        ##Repress
        if airlock_pump_voltage == 0 and airlock_pump_switch == 0 and crewlockpres >= 3 and crewlockpres < 734 and int(stationmode) == 5:
            eva = False
            self.us_eva.ids.EVA_occuring.color = 0, 0, 1
            self.us_eva.ids.EVA_occuring.text = "Crewlock Repressurizing"
            self.us_eva.ids.Crewlock_Status_image.source = '/home/pi/Mimic/Pi/imgs/eva/RepressLights.png'

        ##-------------------RS EVA Functionality-------------------##
        ##if eva station mode and not us eva
        if airlock_pump_voltage == 0 and crewlockpres >= 734 and stationmode == 5:
            rsevaflashevent = Clock.schedule_once(self.flashRS_EVAbutton, 1)


        ##-------------------EVA Functionality End-------------------##

#        if (difference > -10) and (isinstance(App.get_running_app().root_window.children[0], Popup)==False):
#            LOSpopup = Popup(title='Loss of Signal', content=Label(text='Possible LOS Soon'), size_hint=(0.3, 0.2), auto_dismiss=True)
#            LOSpopup.open()
#            print "popup"

        ##-------------------Fake Orbit Simulator-------------------##
        self.fakeorbit_screen.ids.psarj.text = str(psarj)
        self.fakeorbit_screen.ids.ssarj.text = str(ssarj)
        self.fakeorbit_screen.ids.beta1a.text = str(beta1a)
        self.fakeorbit_screen.ids.beta1b.text = str(beta1b)
        self.fakeorbit_screen.ids.beta2a.text = str(beta2a)
        self.fakeorbit_screen.ids.beta2b.text = str(beta2b)
        self.fakeorbit_screen.ids.beta3a.text = str(beta3a)
        self.fakeorbit_screen.ids.beta3b.text = str(beta3b)
        self.fakeorbit_screen.ids.beta4a.text = str(beta4a)
        self.fakeorbit_screen.ids.beta4b.text = str(beta4b)

        if demoboolean:
            self.serialWrite("PSARJ=" + str(psarj) + " ")
            self.serialWrite("SSARJ=" + str(ssarj) + " ")
            self.serialWrite("Beta1B=" + str(beta1b) + " ")
            self.serialWrite("Beta1A=" + str(beta1a) + " ")
            self.serialWrite("Beta2B=" + str(beta2b) + " ")
            self.serialWrite("Beta2A=" + str(beta2a) + " ")
            self.serialWrite("Beta3B=" + str(beta3b) + " ")
            self.serialWrite("Beta3A=" + str(beta3a) + " ")
            self.serialWrite("Beta4B=" + str(beta4b) + " ")
            self.serialWrite("Beta4A=" + str(beta4a) + " ")

        self.eps_screen.ids.psarj_value.text = psarj + "deg"
        self.eps_screen.ids.ssarj_value.text = ssarj + "deg"
        self.tcs_screen.ids.ptrrj_value.text = ptrrj + "deg"
        self.tcs_screen.ids.strrj_value.text = strrj + "deg"
        self.eps_screen.ids.beta1b_value.text = beta1b
        self.eps_screen.ids.beta1a_value.text = beta1a
        self.eps_screen.ids.beta2b_value.text = beta2b
        self.eps_screen.ids.beta2a_value.text = beta2a
        self.eps_screen.ids.beta3b_value.text = beta3b
        self.eps_screen.ids.beta3a_value.text = beta3a
        self.eps_screen.ids.beta4b_value.text = beta4b
        self.eps_screen.ids.beta4a_value.text = beta4a
        self.eps_screen.ids.c1a_value.text = c1a + "A"
        self.eps_screen.ids.v1a_value.text = v1a + "V"
        self.eps_screen.ids.c1b_value.text = c1b + "A"
        self.eps_screen.ids.v1b_value.text = v1b + "V"
        self.eps_screen.ids.c2a_value.text = c2a + "A"
        self.eps_screen.ids.v2a_value.text = v2a + "V"
        self.eps_screen.ids.c2b_value.text = c2b + "A"
        self.eps_screen.ids.v2b_value.text = v2b + "V"
        self.eps_screen.ids.c3a_value.text = c3a + "A"
        self.eps_screen.ids.v3a_value.text = v3a + "V"
        self.eps_screen.ids.c3b_value.text = c3b + "A"
        self.eps_screen.ids.v3b_value.text = v3b + "V"
        self.eps_screen.ids.c4a_value.text = c4a + "A"
        self.eps_screen.ids.v4a_value.text = v4a + "V"
        self.eps_screen.ids.c4b_value.text = c4b + "A"
        self.eps_screen.ids.v4b_value.text = v4b + "V"
        self.iss_screen.ids.altitude_value.text = str(altitude) + " km"
        self.iss_screen.ids.velocity_value.text = str(velocity) + " m/s"
        self.iss_screen.ids.stationmass_value.text = str(iss_mass) + " kg"

        self.us_eva.ids.EVA_needle.angle = float(self.map_rotation(0.0193368*float(crewlockpres)))
        self.us_eva.ids.crewlockpressure_value.text = "{:.2f}".format(0.0193368*float(crewlockpres))

        psi_bar_x = self.map_psi_bar(0.0193368*float(crewlockpres)) #convert to torr

        self.us_eva.ids.EVA_psi_bar.pos_hint = {"center_x": psi_bar_x, "center_y": 0.56}

        
        ##-------------------Signal Status Check-------------------##

        if client_status.split(":")[0] == "Connected": 
            if sub_status == "Subscribed":
                #client connected and subscibed to ISS telemetry
                if float(aos) == 1.00:
                    self.signal_acquired() #signal status 1 means acquired

                elif float(aos) == 0.00:
                    self.signal_lost() #signal status 0 means loss of signal
                
                elif float(aos) == 2.00:
                    self.signal_stale() #signal status 2 means data is not being updated from server
            else:
                self.signal_unsubscribed()
        else:
            self.signal_unsubscribed()

        if mimicbutton: # and float(aos) == 1.00):
            self.serialWrite("PSARJ=" + psarj + " ")
            self.serialWrite("SSARJ=" + ssarj + " ")
            self.serialWrite("PTRRJ=" + ptrrj + " ")
            self.serialWrite("STRRJ=" + strrj + " ")
            self.serialWrite("Beta1B=" + beta1b + " ")
            self.serialWrite("Beta1A=" + beta1a + " ")
            self.serialWrite("Beta2B=" + beta2b + " ")
            self.serialWrite("Beta2A=" + beta2a + " ")
            self.serialWrite("Beta3B=" + beta3b + " ")
            self.serialWrite("Beta3A=" + beta3a + " ")
            self.serialWrite("Beta4B=" + beta4b + " ")
            self.serialWrite("Beta4A=" + beta4a + " ")
            self.serialWrite("AOS=" + aos + " ")
            self.serialWrite("Voltage1A=" + v1a + " ")
            self.serialWrite("Voltage2A=" + v2a + " ")
            self.serialWrite("Voltage3A=" + v3a + " ")
            self.serialWrite("Voltage4A=" + v4a + " ")
            self.serialWrite("Voltage1B=" + v1b + " ")
            self.serialWrite("Voltage2B=" + v2b + " ")
            self.serialWrite("Voltage3B=" + v3b + " ")
            self.serialWrite("Voltage4B=" + v4b + " ")

        #data to send regardless of signal status
        if mimicbutton:
            self.serialWrite("Module=" + module + " ")

#All GUI Screens are on separate kv files
Builder.load_file('/home/pi/Mimic/Pi/Screens/Settings_Screen.kv')
Builder.load_file('/home/pi/Mimic/Pi/Screens/FakeOrbitScreen.kv')
Builder.load_file('/home/pi/Mimic/Pi/Screens/Orbit_Screen.kv')
Builder.load_file('/home/pi/Mimic/Pi/Screens/ISS_Screen.kv')
Builder.load_file('/home/pi/Mimic/Pi/Screens/ECLSS_Screen.kv')
Builder.load_file('/home/pi/Mimic/Pi/Screens/EPS_Screen.kv')
Builder.load_file('/home/pi/Mimic/Pi/Screens/CT_Screen.kv')
Builder.load_file('/home/pi/Mimic/Pi/Screens/CT_SGANT_Screen.kv')
Builder.load_file('/home/pi/Mimic/Pi/Screens/CT_SASA_Screen.kv')
Builder.load_file('/home/pi/Mimic/Pi/Screens/CT_UHF_Screen.kv')
Builder.load_file('/home/pi/Mimic/Pi/Screens/CT_Camera_Screen.kv')
Builder.load_file('/home/pi/Mimic/Pi/Screens/GNC_Screen.kv')
Builder.load_file('/home/pi/Mimic/Pi/Screens/TCS_Screen.kv')
Builder.load_file('/home/pi/Mimic/Pi/Screens/EVA_US_Screen.kv')
Builder.load_file('/home/pi/Mimic/Pi/Screens/EVA_RS_Screen.kv')
Builder.load_file('/home/pi/Mimic/Pi/Screens/EVA_Main_Screen.kv')
Builder.load_file('/home/pi/Mimic/Pi/Screens/EVA_Pictures.kv')
Builder.load_file('/home/pi/Mimic/Pi/Screens/Crew_Screen.kv')
Builder.load_file('/home/pi/Mimic/Pi/Screens/RS_Screen.kv')
Builder.load_file('/home/pi/Mimic/Pi/Screens/ManualControlScreen.kv')
Builder.load_file('/home/pi/Mimic/Pi/Screens/MimicScreen.kv')
Builder.load_file('/home/pi/Mimic/Pi/Screens/CalibrateScreen.kv')
Builder.load_file('/home/pi/Mimic/Pi/Screens/MainScreen.kv')

Builder.load_string('''
#:kivy 1.8
#:import kivy kivy
#:import win kivy.core.window
ScreenManager:
    Settings_Screen:
    FakeOrbitScreen:
    Orbit_Screen:
    EPS_Screen:
    CT_Screen:
    CT_SASA_Screen:
    CT_UHF_Screen:
    CT_Camera_Screen:
    CT_SGANT_Screen:
    ISS_Screen:
    ECLSS_Screen:
    GNC_Screen:
    TCS_Screen:
    EVA_US_Screen:
    EVA_RS_Screen:
    EVA_Main_Screen:
    EVA_Pictures:
    RS_Screen:
    Crew_Screen:
    ManualControlScreen:
    MimicScreen:
    CalibrateScreen:
    MainScreen:
''')

if __name__ == '__main__':
    MainApp().run()
