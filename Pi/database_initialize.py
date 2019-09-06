import sqlite3 #javascript stores telemetry in sqlite db
import os

#----------------Open SQLITE3 Database that holds the current ISS Telemetry--------------
os.system('rm /dev/shm/iss_telemetry.db') #delete sqlite database on exit, db is recreated each time to avoid concurrency issues
conn = sqlite3.connect('/dev/shm/iss_telemetry.db')
conn.isolation_level = None
c = conn.cursor()
#now we populate the blank database, this prevents locked database issues
c.execute("pragma journal_mode=wal");
c.execute("CREATE TABLE IF NOT EXISTS telemetry (`Label` TEXT PRIMARY KEY, `Timestamp` TEXT, `Value` TEXT, `ID` TEXT, `dbID` NUMERIC )");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('psarj', '0', '0', 'S0000004', 0)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('ssarj', '0', '0', 'S0000003', 1)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('ptrrj', '0', '0', 'S0000002', 2)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('strrj', '0', '5', 'S0000001', 3)");
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
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS MT Position Float', '0', '0', 'CSAMT000001', 257)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS MT Utility Port ID', '0', '0', 'CSAMT000001', 258)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS EDCD SSRMS Base Location', '0', '0', 'CSASSRMS001', 259)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS EDCD SSRMS Base Location', '0', '0', 'CSASSRMS002', 260)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS EDCD SSRMS Operating Base', '0', '0', 'CSASSRMS003', 261)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('SSRMS SR Measured Joint Position', '0', '0', 'CSASSRMS004', 262)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('SSRMS SY Measured Joint Position', '0', '0', 'CSASSRMS005', 263)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('SSRMS SP Measured Joint Position', '0', '0', 'CSASSRMS006', 264)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('SSRMS EP Measured Joint Position', '0', '0', 'CSASSRMS007', 265)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('SSRMS WP Measured Joint Position', '0', '0', 'CSASSRMS008', 266)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('SSRMS WY Measured Joint Position', '0', '0', 'CSASSRMS009', 267)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('SSRMS WR Measured Joint Position', '0', '0', 'CSASSRMS010', 268)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS OCS Payload Status SSRMS Tip LEE', '0', '0', 'CSASSRMS011', 269)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS OCS Base Location SPDM', '0', '0', 'CSASPDM0001', 270)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS OCS Base Location SPDM', '0', '0', 'CSASPDM0002', 271)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS OCS SPDM 1 SR Measured Joint Position', '0', '0', 'CSASPDM0003', 272)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS OCS SPDM 1 SY Measured Joint Position', '0', '0', 'CSASPDM0004', 273)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS OCS SPDM 1 SP Measured Joint Position', '0', '0', 'CSASPDM0005', 274)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS OCS SPDM 1 EP Measured Joint Position', '0', '0', 'CSASPDM0006', 275)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS OCS SPDM 1 WP Measured Joint Position', '0', '0', 'CSASPDM0007', 276)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS OCS SPDM 1 WY Measured Joint Position', '0', '0', 'CSASPDM0008', 277)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS OCS SPDM 1 WR Measured Joint Position', '0', '0', 'CSASPDM0009', 278)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS Payload Status OCS SPDM Arm 1 OTCM', '0', '0', 'CSASPDM0010', 279)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS OCS SPDM 2 SR Measured Joint Position', '0', '0', 'CSASPDM0011', 280)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS OCS SPDM 2 SY Measured Joint Position', '0', '0', 'CSASPDM0012', 281)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS OCS SPDM 2 SP Measured Joint Position', '0', '0', 'CSASPDM0013', 282)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS OCS SPDM 2 EP Measured Joint Position', '0', '0', 'CSASPDM0014', 283)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS OCS SPDM 2 WP Measured Joint Position', '0', '0', 'CSASPDM0015', 284)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS OCS SPDM 2 WY Measured Joint Position', '0', '0', 'CSASPDM0016', 285)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS OCS SPDM 2 WR Measured Joint Position', '0', '0', 'CSASPDM0017', 286)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS Payload Status OCS SPDM Arm 2 OTCM', '0', '0', 'CSASPDM0018', 287)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS Payload Status OCS SPDM Arm 2 OTCM2', '0', '0', 'CSASPDM0019', 288)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS OCS SPDM Body Roll Joint Position', '0', '0', 'CSASPDM0020', 289)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS Payload Status OCS SPDM Body', '0', '0', 'CSASPDM0021', 290)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS Payload Status OCS SPDM Body2', '0', '0', 'CSASPDM0022', 291)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS OCS Payload Status MBS MCAS', '0', '0', 'CSAMBS00001', 292)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS OCS Payload Status MBS MCAS2', '0', '0', 'CSAMBS00002', 293)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS OCS Payload Status MBS POA', '0', '0', 'CSAMBS00003', 294)");
c.execute("INSERT OR IGNORE INTO telemetry VALUES('MSS OCS Payload Status MBS POA2', '0', '0', 'CSAMBA00004', 295)");
conn.close()
