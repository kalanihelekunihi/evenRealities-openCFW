"""
Cordio BLE stack function upgrades for ota_s200_firmware_ota decompilation.
Identified from LOW confidence entries in ble, ble.comm, ble.smpdb, ble.smp,
ble.dm, ble.att, ble.cordio, ble.phy, ble.ll, ble.master modules.

Generated: 2026-03-07
Source: decompiled.c + function_map.txt analysis
"""

upgrades = {
    # =====================================================================
    # HCI Core — vtable dispatch wrappers and init
    # =====================================================================
    '0x00479256': ('hciDrvRecvCback', 'ble.hci', 'MED', '# HCI transport vtable[0x2c] dispatch — recv callback # was: ble_callee_9256'),
    '0x00479268': ('hciDrvGetNumBufs', 'ble.hci', 'MED', '# HCI transport vtable[0x20] dispatch — get num bufs # was: ble_callee_9268'),
    '0x0047927e': ('hciDrvReadBufSize', 'ble.hci', 'MED', '# HCI transport vtable[0x24] dispatch — read buf size(connId,phy) # was: ble_callee_927e'),
    '0x00479298': ('hciDrvGetNumCmplPkts', 'ble.hci', 'MED', '# HCI transport vtable[0x28] dispatch — num completed pkts # was: ble_callee_9298'),
    '0x004792ae': ('hciDrvVsSpecific', 'ble.hci', 'MED', '# HCI transport vtable[0x30] dispatch — VS specific # was: ble_callee_92ae'),
    '0x004792c4': ('hciDrvGetSupFeatures', 'ble.hci', 'MED', '# HCI transport vtable[0x34] dispatch — supported features # was: ble_callee_92c4'),
    '0x004792da': ('hciDrvGetAdvTxPower', 'ble.hci', 'MED', '# HCI transport vtable[0x38] dispatch — adv TX power # was: ble_callee_92da'),
    '0x00479b12': ('hciCoreGetPhySupport', 'ble.hci', 'MED', '# reads PHY support flags: 0=none, 1=1M, 2=coded # was: ble_callee_9b12'),
    '0x00479d94': ('hciEvtMaskGetWordAndBit', 'ble.hci', 'HIGH', '# computes word=param>>5, mask=1<<(param&0x1f) for event mask # was: ble_callee_9d94'),

    # =====================================================================
    # HCI Core — command queue and init
    # =====================================================================
    '0x00498496': ('hciCoreCmdBufInit', 'ble.hci', 'HIGH', '# ring buffer init: 0x104 item size, 0x820 total (8 HCI cmd slots) # was: ble_neighbor_00498728_wrapper'),
    '0x00498b40': ('AttcMtuReq', 'ble.att', 'HIGH', '# builds ATT_MTU_REQ PDU (opcode=2), sends via L2CAP # was: ble_callee_8b40'),
    '0x00498ef4': ('DmDevReset', 'ble.dm', 'HIGH', '# calls dmPrivInit + dmConnInit + dmDevCccInit + dmDevInit # was: ble_callee_8ef4'),
    '0x004980de': ('hciCoreConnClose', 'ble.hci', 'MED', '# clears timers, resets counters, closes LL channel # was: ble_callee_80de'),

    # =====================================================================
    # HCI command sending and version checking
    # =====================================================================
    '0x00495784': ('HciLeSetPhy', 'ble.hci', 'MED', '# HCI LE command wrapper, builds cmd with conn handle + PHY params # was: ble_callee_5784'),
    '0x004957c4': ('HciLeReadPhy', 'ble.hci', 'MED', '# HCI LE command wrapper, reads PHY for connection # was: ble_callee_57c4'),
    '0x004958b0': ('hciCoreConnParamInit', 'ble.hci', 'MED', '# inits default conn params: interval=0x640, timeout=0x780, latency=7 # was: ble_callee_58b0'),
    '0x004958fc': ('hciCoreConnParamReset', 'ble.hci', 'MED', '# resets conn param defaults per handle slot # was: ble_callee_58fc'),

    # =====================================================================
    # DM Advertising state machine
    # =====================================================================
    '0x0049d3e8': ('dmAdvInit', 'ble.dm_adv', 'HIGH', '# resets adv state, sets initial state table ptr # was: ble_callee_d3e8'),
    '0x0049d90e': ('DmAdvStop', 'ble.dm_adv', 'HIGH', '# sends DM internal msg event=0x13 (ADV_STOP) # was: ble_callee_d90e'),
    '0x0049d91e': ('dmAdvFindActive', 'ble.dm_adv', 'HIGH', '# scans 3 adv sets (0x30 stride) for first active # was: module_callee_00473F52'),
    '0x004e3214': ('dmPrivClearResList', 'ble.dm_priv', 'HIGH', '# resets 10-entry resolving list (0xF stride) # was: ble_callee_3214'),
    '0x004e323c': ('dmPrivAddDevToResList', 'ble.dm_priv', 'HIGH', '# adds device to resolving list, copies addr+IRK # was: ble_callee_323c'),
    '0x004e32f0': ('dmPrivFindInResList', 'ble.dm_priv', 'HIGH', '# finds device in resolving list by addr type+addr # was: ble_callee_32f0'),
    '0x004e3342': ('dmAdvActResetResList', 'ble.dm_adv', 'MED', '# clears resolving list on HCI reset # was: ble_callee_3342'),
    '0x004e3528': ('dmAdvActAddDev', 'ble.dm_adv', 'MED', '# wrapper: adds device to resolving list # was: ble_callee_3528'),
    '0x004e3530': ('dmAdvActStart', 'ble.dm_adv', 'MED', '# starts advertising on set # was: ble_callee_3530'),
    '0x004e353c': ('dmAdvActSetDataComplete', 'ble.dm_adv', 'MED', '# handles adv data set completion, clears pending flag # was: ble_callee_353c'),
    '0x004e3556': ('dmAdvActConfig', 'ble.dm_adv', 'MED', '# configures advertising set parameters # was: ble_callee_3556'),
    '0x004e357c': ('dmAdvActTimerExpiry', 'ble.dm_adv', 'MED', '# handles adv timer expiration # was: ble_callee_357c'),
    '0x004e358c': ('dmAdvActAdvComplete', 'ble.dm_adv', 'MED', '# handles advertising complete event # was: ble_callee_358c'),
    '0x004e35d8': ('dmAdvActSetRandAddr', 'ble.dm_adv', 'MED', '# sets random BLE address for advertising # was: ble_callee_35d8'),
    '0x004e35ec': ('dmAdvActEnableTimeout', 'ble.dm_adv', 'MED', '# enables adv timeout timer # was: ble_callee_35ec'),
    '0x004e360a': ('dmAdvActDisableTimeout', 'ble.dm_adv', 'MED', '# disables adv timeout timer # was: ble_callee_360a'),
    '0x004e3624': ('dmAdvActUpdateParam', 'ble.dm_adv', 'MED', '# updates advertising parameters # was: ble_callee_3624'),
    '0x004e3646': ('dmAdvActSetAdvEnable', 'ble.dm_adv', 'MED', '# enables advertising, sends conn param update # was: ble_callee_3646'),
    '0x004e3678': ('dmAdvActStop', 'ble.dm_adv', 'MED', '# stops advertising on set, sends DmAdvStop # was: ble_callee_3678'),
    '0x004e3890': ('dmAdvActConnParamUpdate', 'ble.dm_adv', 'MED', '# sends conn param update req after adv connect # was: ble_callee_3890'),
    '0x004e38e2': ('dmPrivInit', 'ble.dm_priv', 'HIGH', '# initializes privacy state: clears pending, resets index # was: ble_callee_38e2'),
    '0x004e3ea4': ('DmPrivResolveAddr', 'ble.dm_priv', 'MED', '# resolves address against resolving list entries # was: ble_callee_3ea4'),
    '0x004e3fc4': ('AppAdvSetData', 'ble.dm_adv', 'MED', '# sets advertising data using app-level API # was: module_callee_004DEEB6'),

    # =====================================================================
    # DM Connection state machine actions
    # =====================================================================
    '0x00496bf4': ('dmConnSmActOpen', 'ble.dm_conn', 'HIGH', '# opens connection: configures PHY, sets adv params # was: ble_callee_6bf4'),
    '0x00496c98': ('dmConnSmActUpdateParam', 'ble.dm_conn', 'MED', '# updates connection parameters # was: ble_callee_6c98'),
    '0x00496cba': ('dmConnSmActSetAdvEnable', 'ble.dm_conn', 'MED', '# enables advertising for connection # was: ble_callee_6cba'),
    '0x00496d10': ('dmConnSmActNone', 'ble.dm_conn', 'HIGH', '# no-op action (empty function) # was: ble_callee_6d10'),
    '0x00496d12': ('dmConnSmActConnOpened', 'ble.dm_conn', 'HIGH', '# handles connection opened: sets CCC, notifies app # was: ble_callee_6d12'),
    '0x00496d7c': ('dmConnSmActAcceptOpen', 'ble.dm_conn', 'MED', '# accepts incoming connection request # was: ble_callee_6d7c'),
    '0x00496de0': ('dmConnSmActSetRandAddr', 'ble.dm_conn', 'MED', '# sets random address for connection # was: ble_callee_6de0'),
    '0x00496df4': ('dmConnSmActEnableTimeout', 'ble.dm_conn', 'MED', '# enables connection timeout timer # was: ble_callee_6df4'),
    '0x00496e12': ('dmConnSmActDisableTimeout', 'ble.dm_conn', 'MED', '# disables connection timeout timer # was: ble_callee_6e12'),

    # =====================================================================
    # DM Scanning state machine
    # =====================================================================
    '0x004e55ee': ('dmScanActComplete', 'ble.dm_scan', 'MED', '# transitions scan state 2->3, resets BLE # was: ble.comm_neighbor_004e55ee'),
    '0x004e560e': ('dmScanProcAdvReport', 'ble.dm_scan', 'MED', '# processes advertising report during scanning # was: ble.comm_neighbor_004e560e'),
    '0x004e5670': ('dmScanActStop', 'ble.dm_scan', 'MED', '# stops scanning, sends event 0x25 (scan stop) # was: ble.comm_neighbor_004e5670'),
    '0x004e5730': ('dmScanSmExecute', 'ble.dm_scan', 'HIGH', '# scan SM dispatch: vtable[event & 7] # was: ble.comm_propagated_004e5730'),
    '0x004e5d7c': ('dmConnPrivInit', 'ble.dm_priv', 'MED', '# initializes 3 connection privacy entries # was: ble_callee_5d7c'),

    # =====================================================================
    # DM Device Manager init and reset
    # =====================================================================
    '0x004e42d4': ('dmExtAdvActScanReport', 'ble.dm', 'MED', '# handles ext adv report event (type 0x12) # was: ble_callee_42d4'),
    '0x004e432e': ('dmDevActCccInit', 'ble.dm', 'MED', '# calls AttsCccInit to init CCC table # was: ble_callee_432e'),
    '0x004e43d6': ('dmConnGetCfg', 'ble.dm', 'MED', '# returns pointer to connection config (0x60 bytes) # was: ble_callee_43d6'),
    '0x004e43da': ('DmSecSlaveReq', 'ble.dm', 'HIGH', '# allocates WSF msg, sends SMP_MSG_API_SECURITY_REQ (event 0x16) # was: ble_callee_43da'),
    '0x004e4412': ('DmPrivAddrHash', 'ble.dm_priv', 'MED', '# computes address hash via modulo for resolving # was: ble_callee_4412'),
    '0x004e4454': ('dmDevMsgHandlerInit', 'ble.dm', 'MED', '# sets up DM device SM callback tables # was: ble_callee_4454'),
    '0x004e2428': ('dmDevResetCb', 'ble.dm', 'HIGH', '# initializes 3 device entries (0x10 stride), clears state # was: ble_callee_2428'),
    '0x004e7104': ('SmpInit', 'ble.smp', 'HIGH', '# sets SMP state machine action tables (offsets 0xE8,0xF0,0xF4) # was: ble_callee_7104'),

    # =====================================================================
    # ATT Server (atts)
    # =====================================================================
    '0x00487a5a': ('attsWriteRspSetup', 'ble.att', 'MED', '# sets up ATT_WRITE_RSP (opcode 0x20) PDU # was: ble_att_callee_7a5a'),
    '0x00487c00': ('attsCsfCalcDbSize', 'ble.att', 'MED', '# calculates GATT DB attribute entry size for CSF hash # was: ble_callee_7c00'),
    '0x004880e8': ('attsL2cDataReq', 'ble.att', 'HIGH', '# thin wrapper: sends ATT data via L2cDataReq # was: ble_comm_callee_80e8'),
    '0x004d0c6c': ('attsFindByHandle', 'ble.att', 'HIGH', '# walks GATT attr DB linked list, finds by handle range # was: ble_callee_0c6c'),
    '0x004d0d1c': ('attsFindNextService', 'ble.att', 'MED', '# searches for next service UUID handle after param # was: ble_callee_0d1c'),
    '0x005261b4': ('attsRemoveGroupStub', 'ble.att', 'MED', '# stub: returns 0 (no-op) # was: atts_callee_61b4'),
    '0x005261c8': ('attsRemoveGroupNop', 'ble.att', 'MED', '# empty function — no-op stub # was: atts_callee_61c8'),
    '0x005261ea': ('mathDivHelper', 'ble.math', 'LOW', '# FP division helper, misclassified as ATT # was: atts_callee_61ea'),

    # =====================================================================
    # ATT Client (attc) — discovery and PDU building
    # =====================================================================
    '0x0052a09a': ('attcDiscInit', 'ble.att', 'MED', '# thin wrapper calling attcDiscServiceInit # was: ble_callee_a09a'),
    '0x0052a0a4': ('attcDiscProcFindInfo', 'ble.att', 'MED', '# parses handle ranges from ATT response, validates ordering # was: ble_neighbor_0052a0a4'),
    '0x0052a148': ('attcDiscCharProcAdjust', 'ble.att', 'MED', '# updates discovery progress handle range # was: ble_neighbor_0052a148'),
    '0x0052a172': ('AttcReadByTypeReq', 'ble.att', 'HIGH', '# builds ATT_READ_BY_TYPE_REQ (opcode 6), sends via L2CAP # was: ble_callee_a172'),
    '0x0052a3bc': ('smpScAllocKeyBufs', 'ble.smp', 'HIGH', '# allocates 5 SMP SC key buffers (0x60,0x40,0x20,0x40,0x20) # was: ble_callee_a3bc'),
    '0x0052a570': ('SmpScInit', 'ble.smp', 'HIGH', '# initializes 3 SMP SC connection CBs (0x4C stride, SC at +0x48) # was: ble_callee_a570'),

    # =====================================================================
    # SMP — Security Manager Protocol
    # =====================================================================
    '0x0052a44a': ('smpScFreeKeyBufs', 'ble.smp', 'HIGH', '# frees 5 SMP SC key buffers at offsets 0x14,0x08,0x18,0x0C,0x10 # was: module_callee_005C7FFC'),
    '0x0052b0e2': ('DmConnSetDataLen', 'ble.dm_conn', 'MED', '# WSF msg event=0x10 (DATA_LEN_CHANGE), sets key distribution # was: ble_callee_b0e2'),
    '0x0052b152': ('DmReset', 'ble.dm', 'HIGH', '# WSF msg event=0x11 (DM_RESET), sends internal reset # was: ble_callee_b152'),
    '0x0052b16e': ('DmConnSetConnSpec', 'ble.dm_conn', 'MED', '# sets connection interval/timeout per connId # was: ble_callee_b16e'),
    '0x0052b19c': ('DmConnSetPhyConnSpec', 'ble.dm_conn', 'MED', '# iterates PHY bit flags, sets conn spec per PHY # was: ble_callee_b19c'),
    '0x0052b54c': ('smpActSendSecurityReq', 'ble.smp', 'HIGH', '# sends SMP security req (event 0x2E) or error (event 4, reason 3) # was: module_callee_0052BC0C_b54c'),
    '0x005c7f8a': ('smpScActSendSecurityReq', 'ble.smp', 'HIGH', '# SC variant: checks SC CB before sending security req # was: module_callee_0052BC0C_7f8a'),
    '0x005c7ffc': ('smpScActCleanup', 'ble.smp', 'HIGH', '# calls smpScResetState + smpScFreeKeyBufs # was: module_callee_005C800E'),
    '0x005c800e': ('smpScActCleanupAndReset', 'ble.smp', 'HIGH', '# calls smpScActCleanup + smpSmReset # was: module_callee_0052B352'),
    '0x005c803e': ('smpScActCalcDHKeyRsp', 'ble.smp', 'MED', '# copies DH keys, selects LTK type (0x13/0x14/0x15), dispatches # was: module_callee_0052BC0C_803e'),
    '0x005c818a': ('smpScActCalcSharedSecret', 'ble.smp', 'MED', '# builds 0x50-byte buf with initiator/responder keys for DH # was: module_callee_0052A4BE'),
    '0x004cd554': ('smpScActClearFlags', 'ble.smp', 'MED', '# clears SC flag bit 0 and returns 0 # was: module_callee_004BC7CE'),
    '0x004cc444': ('SmpDmApiPairReq', 'ble.smp', 'HIGH', '# WSF msg event=4 (SMP_MSG_API_PAIR_REQ), copies pairing data # was: ble_comm_callee_c444'),

    # =====================================================================
    # SMP DB — pairing database management
    # =====================================================================
    '0x00468d64': ('smpDbFindRecord', 'ble.smpdb', 'HIGH', '# searches 32-entry (0x1F) SMP DB table by param, returns index # was: module_callee_00468DF6'),
    '0x00468df6': ('smpDbAddRecord', 'ble.smpdb', 'HIGH', '# adds SMP DB record: finds/allocates slot, sets active flag # was: module_callee_0046D6E0_8df6'),
    '0x00468e74': ('smpDbRemoveRecord', 'ble.smpdb', 'HIGH', '# removes SMP DB record: finds slot, clears active flag, decrements count # was: module_callee_0046D6E0_8e74'),
    '0x00468ece': ('smpDbHasRecords', 'ble.smpdb', 'MED', '# checks if SMP DB has any active records (count != 0) # was: module_callee_0046D6E0_8ece'),
    '0x004cc820': ('dmSecSendMsg_0x33', 'ble.smpdb', 'MED', '# WSF msg alloc 0x2C, event=0x33 (DM_SEC internal), sends to handler # was: ble.smpdb_neighbor_004cc820'),
    '0x0053b76e': ('smpDbStoreLocalIrk', 'ble.smpdb', 'HIGH', '# stores local IRK: 7 words at +0xA0, addr type at +0xD4 # was: module_callee_0046D6E0_b76e'),
    '0x0053b7d8': ('smpDbStorePeerIrk', 'ble.smpdb', 'HIGH', '# stores peer IRK: 7 words at +0x64, addr type at +0x98 # was: module_callee_0046D6E0_b7d8'),
    '0x0056eb0c': ('smpDbCalcTxPowerAdj', 'ble.smpdb', 'MED', '# calculates TX power adjustment based on link quality (0/1/2) # was: module_callee_0056EBB8_eb0c'),
    '0x0056ebb8': ('smpDbSetTxPower', 'ble.smpdb', 'MED', '# sets TX power level with interrupt-safe write # was: module_callee_0046D6E0_ebb8'),
    '0x0056ebec': ('smpDbPhyRateSelect', 'ble.smpdb', 'MED', '# selects PHY rate based on float thresholds (RSSI ranges) # was: module_callee_0056EBB8_ebec'),

    # =====================================================================
    # DM Security — connection level
    # =====================================================================
    '0x0048b5f4': ('dmSecCompareSecLevel', 'ble.dm', 'HIGH', '# compares security levels: 1=NoMITM, 2=MITM → effective level # was: ble_callee_b5f4'),
    '0x0048b640': ('dmSecCompareSecLevel2', 'ble.dm', 'MED', '# identical to dmSecCompareSecLevel — duplicate for second path # was: ble_callee_b640'),
    '0x0048b67e': ('dmSecCompareSecLevelWrapper', 'ble.dm', 'MED', '# wrapper: calls dmSecCompareSecLevel2(2, param) # was: ble_callee_b67e'),
    '0x0048b572': ('dmSecGetSecLevel', 'ble.dm', 'MED', '# returns current security level # was: ble_callee_b572'),
    '0x0048b68c': ('dmSecClearKeys', 'ble.dm', 'MED', '# wrapper: calls dmSecKeysClear # was: ble_callee_b68c'),
    '0x004cc710': ('DmSecInit', 'ble.dm', 'HIGH', '# stores conn info, calls DM security init # was: module_callee_0048B3E2'),
    '0x0048bacc': ('dmConnSmCallCback', 'ble.dm', 'MED', '# calls through conn SM callback at offset 0x34+8 # was: ble_callee_bacc'),

    # =====================================================================
    # WSF — Wireless Software Foundation utilities
    # =====================================================================
    '0x00488396': ('WsfTaskSetReady', 'ble.wsf', 'HIGH', '# sets ready bits at offset 0x28+connId, flags byte at 0x3C # was: ble_callee_8396'),
    '0x00488416': ('WsfTaskIsIdle', 'ble.wsf', 'HIGH', '# returns true if flag byte at 0x3C is zero # was: ble_callee_8416'),
    '0x004dfcc4': ('WsfRingBufWrite', 'ble.wsf', 'HIGH', '# ring buffer write: param_3 items of param_1[4] size # was: ble_callee_fcc4'),
    '0x004dfd22': ('WsfRingBufRead', 'ble.wsf', 'HIGH', '# ring buffer read: drains items from circular buffer # was: ble_callee_fd22'),
    '0x004a2264': ('WsfBufAppend', 'ble.wsf', 'MED', '# appends data to buffer, advances write pointer # was: module_callee_00439BE4_2264'),

    # =====================================================================
    # L2CAP
    # =====================================================================
    '0x004e61e4': ('L2cCocConnUpdateRsp', 'ble.l2c', 'HIGH', '# builds L2C PDU opcode=0x13 (CONN_UPDATE_RSP), sends # was: module_callee_004CFC60'),

    # =====================================================================
    # Security — crypto and random
    # =====================================================================
    '0x004e531a': ('SecRandRead', 'ble.sec', 'HIGH', '# reads from 32-entry circular PRNG buffer, advances index # was: ble_callee_531a'),
    '0x004e53c8': ('SecTokenAlloc', 'ble.sec', 'MED', '# allocates sequential token ID, skips 0xFF # was: ble_callee_53c8'),
    '0x004e53f2': ('SecAesReq', 'ble.sec', 'HIGH', '# allocates 0x38 WSF msg, assigns token, initiates AES crypto # was: ble_callee_53f2'),
    '0x004e54d2': ('SecEccGenKey', 'ble.sec', 'MED', '# allocates 0x9C WSF msg, type=2, triggers ECC key generation # was: ble_callee_54d2'),

    # =====================================================================
    # HCI event registration and LL
    # =====================================================================
    '0x004da09c': ('hciLeEvtInit', 'ble.hci', 'MED', '# registers HCI event handlers: 0x5D (LE meta), 0x8A (disconnect) # was: ble_callee_a09c'),
    '0x004da232': ('hciCoreChannelClose', 'ble.hci', 'MED', '# closes BLE connection channel, frees resources # was: ble_callee_a232'),
    '0x004db1ee': ('hciEvtRegDisconnect', 'ble.hci', 'MED', '# registers/unregisters HCI disconnect event (0x88) handler # was: ble_callee_b1ee'),

    # =====================================================================
    # ATT CCC (Client Characteristic Configuration)
    # =====================================================================
    '0x004dec0a': ('AttcCccSet', 'ble.att', 'HIGH', '# sets CCC value for connId at table index # was: ble_callee_ec0a'),
    '0x004dec5c': ('AttcCccGetCount', 'ble.att', 'HIGH', '# returns number of CCC entries from config # was: ble_callee_ec5c'),
    '0x004def04': ('DmPrivSetAddrType', 'ble.dm_priv', 'MED', '# simple setter: stores address type value # was: ble_callee_ef04'),

    # =====================================================================
    # EM9305 Radio / UART
    # =====================================================================
    '0x0053bb9a': ('em9305_uart_write', 'ble.cordio', 'HIGH', '# writes bytes to UART register at base + 0x1000*channel # was: ble_callee_bb9a'),
    '0x0053bc1c': ('em9305_uart_flush', 'ble.cordio', 'MED', '# reads ring buffer, writes to UART — TX drain # was: ble_callee_bc1c'),
    '0x0056f710': ('em9305_bb_channel_busy_check', 'ble.cordio', 'MED', '# checks 16 radio channels for busy state via status regs # was: ble_callee_f710'),
    '0x0056f834': ('em9305_bb_state_transition', 'ble.cordio', 'MED', '# radio state transition logic (idle/TX/RX) # was: ble_callee_f834'),
    '0x0057097c': ('em9305_radio_channel_config', 'ble.cordio', 'MED', '# configures radio channel parameters # was: ble_callee_097c'),

    # =====================================================================
    # PHY layer
    # =====================================================================
    '0x00514e5c': ('hciPhyGetTxPower', 'ble.phy', 'MED', '# table lookup: TX power by PHY index # was: module_callee_005156D0_4e5c'),
    '0x00514e66': ('hciPhyGetRxSens', 'ble.phy', 'MED', '# table lookup: RX sensitivity by PHY index # was: module_callee_005156D0_4e66'),
    '0x00514e70': ('hciPhyGetModIdx', 'ble.phy', 'MED', '# table lookup: modulation index by PHY index (max 5) # was: module_callee_005156D0_4e70'),
    '0x00514e86': ('hciPhyGetCodedRate', 'ble.phy', 'MED', '# table lookup: coded rate by PHY index # was: module_callee_005156D0_4e86'),
    '0x00514efc': ('hciPhyCalcBitRate', 'ble.phy', 'MED', '# calculates bit rate from float params # was: module_callee_0053A90C_4efc'),
    '0x005157ae': ('hciPhyRegisterConfig', 'ble.phy', 'MED', '# PHY register configuration helper # was: module_callee_005156D0_57ae'),
    '0x0056f276': ('em9305_phy_calibration_helper', 'ble.phy', 'MED', '# PHY calibration helper function # was: ble_phy_neighbor_0056f276'),

    # =====================================================================
    # HCI command queue (LL level)
    # =====================================================================
    '0x005149e2': ('hciCmdQueueAlloc', 'ble.hci', 'MED', '# allocates HCI cmd queue entry with magic validation # was: ble_callee_49e2'),
    '0x00514cea': ('hciCmdQueueComplete', 'ble.hci', 'MED', '# completes HCI cmd queue entry, signals via DMB # was: ble_callee_4cea'),
    '0x005153f4': ('hciCmdQueueDequeue', 'ble.hci', 'MED', '# dequeues completed HCI command # was: ble_callee_53f4'),
    '0x00515458': ('hciCmdQueuePeek', 'ble.hci', 'MED', '# peeks at next HCI command in queue # was: ble_callee_5458'),
    '0x005154a8': ('hciCmdQueueGetStatus', 'ble.hci', 'MED', '# returns HCI cmd queue status # was: ble_callee_54a8'),
    '0x0051566a': ('hciCmdQueueProcess', 'ble.hci', 'MED', '# processes pending HCI commands from queue # was: ble_callee_566a'),
    '0x00515a40': ('hciCmdQueueFlush', 'ble.hci', 'MED', '# flushes all pending HCI commands # was: ble_callee_5a40'),

    # =====================================================================
    # ble.comm layer
    # =====================================================================
    '0x004596ec': ('bleCommInit', 'ble.comm', 'MED', '# thin wrapper calling ble_comm_dispatch init # was: module_callee_00499BAC'),

    # =====================================================================
    # SMP Connection management
    # =====================================================================
    '0x004bcba0': ('smpConnClose', 'ble.smp', 'MED', '# SMP conn close: resets state with IRQ-safe pattern # was: ble_callee_cba0'),
    '0x004bcd24': ('smpScConnClose', 'ble.smp', 'MED', '# SMP SC conn close: resets state, sets pending flag # was: ble_callee_cd24'),
    '0x004bce88': ('smpConnCloseCleanup', 'ble.smp', 'MED', '# SMP conn close cleanup: resets secondary state # was: ble_callee_ce88'),
    '0x004bd42c': ('smpConnOpen', 'ble.smp', 'MED', '# SMP connection open handler # was: ble_callee_d42c'),
    '0x004bd64e': ('smpConnParamUpdate', 'ble.smp', 'MED', '# SMP connection parameter update # was: ble_callee_d64e'),
    '0x004bfbca': ('smpPhyUpdate', 'ble.smp', 'MED', '# SMP PHY update handler # was: ble_callee_fbca'),
    '0x004bfbf8': ('smpPhyUpdateComplete', 'ble.smp', 'MED', '# SMP PHY update completion # was: ble_callee_fbf8'),
    '0x004bc580': ('smpDbGetRecordWrapper', 'ble.smp', 'MED', '# wrapper: gets SMP DB record # was: ble_neighbor_004bc5aa_wrapper'),
    '0x004bc5aa': ('smpDbGetRecord', 'ble.smp', 'MED', '# gets SMP DB record by connId # was: ble_neighbor_004bc5aa'),
    '0x004bc6ae': ('smpDbFreeRecord', 'ble.smp', 'MED', '# frees SMP DB record and clears state # was: ble_callee_c6ae'),
    '0x004bd4e4': ('smpConnInit', 'ble.smp', 'MED', '# SMP connection initialization # was: ble_callee_d4e4'),

    # =====================================================================
    # GATT layer
    # =====================================================================
    '0x004e01c4': ('gattDiscInit', 'ble.gatt', 'MED', '# GATT discovery initialization # was: ble.gatt_neighbor_004e01c4'),
    '0x004e01e0': ('gattDiscReset', 'ble.gatt', 'MED', '# GATT discovery reset # was: ble.gatt_neighbor_004e01e0'),
    '0x00454bc4': ('gattServiceRegister', 'ble.gatt', 'MED', '# registers GATT service # was: module_callee_00454978'),

    # =====================================================================
    # Ambiq HAL (not Cordio but in ble module)
    # =====================================================================
    '0x0046e964': ('am_hal_cachectrl_enable', 'ble.hal', 'MED', '# enables Ambiq cache controller with DSB/ISB barriers # was: module_callee_0056FAB4_e964'),
    '0x0046e9aa': ('am_hal_cachectrl_disable', 'ble.hal', 'MED', '# disables Ambiq cache controller with DSB/ISB barriers # was: module_callee_0056FAB4_e9aa'),

    # =====================================================================
    # Connection helpers
    # =====================================================================
    '0x00473944': ('hciCoreConnOpen', 'ble.hci', 'MED', '# opens HCI connection with handle and address # was: ble_callee_3944'),
    '0x0047403e': ('hciCoreTimerCtrl', 'ble.hci', 'MED', '# enables(1) or disables(0) HCI timer for connection # was: ble_callee_403e'),
    '0x00477188': ('hciCoreResetSeq', 'ble.hci', 'MED', '# HCI reset sequence handler # was: ble_callee_7188'),

    # =====================================================================
    # ATT client processing
    # =====================================================================
    '0x0049878c': ('attcProcMsg', 'ble.att', 'HIGH', '# ATT client msg processor: vtable dispatch by opcode, checks min len # was: module_callee_004E0E30'),

    # =====================================================================
    # Misc BLE LOW entries — smaller helpers
    # =====================================================================
    '0x00497af0': ('hciCoreSendAclOrSco', 'ble.hci', 'MED', '# sends ACL/SCO data, handles PHY state transitions # was: ble_callee_7af0'),
    '0x00497ea6': ('WsfTimerStartCallback', 'ble.wsf', 'MED', '# sets timer callback and either calls directly or enqueues via IRQ # was: ble_callee_7ea6'),
    '0x004a1c7c': ('wsfBufPoolInit', 'ble.wsf', 'MED', '# WSF buffer pool initialization # was: ble_callee_1c7c'),
    '0x004a1cc0': ('wsfBufPoolAlloc', 'ble.wsf', 'MED', '# WSF buffer pool allocation # was: ble_callee_1cc0'),
    '0x004a2170': ('wsfBufPoolFree', 'ble.wsf', 'MED', '# WSF buffer pool free # was: ble_callee_2170'),
    '0x004a2242': ('wsfBufPoolGetSize', 'ble.wsf', 'MED', '# WSF buffer pool get size # was: ble_callee_2242'),
    '0x004a06a8': ('wsfMsgQueuePush', 'ble.wsf', 'MED', '# pushes message onto WSF message queue # was: ble_callee_06a8'),
    '0x004a1038': ('wsfMsgQueuePop', 'ble.wsf', 'MED', '# pops message from WSF message queue # was: ble_callee_1038'),
    '0x004a105a': ('wsfMsgQueuePeek', 'ble.wsf', 'MED', '# peeks at head of WSF message queue # was: ble_callee_105a'),

    # =====================================================================
    # Remaining ble.cordio LOW entries
    # =====================================================================
    '0x00498e0a': ('em9305_hci_cmd_send', 'ble.cordio', 'MED', '# sends HCI command to EM9305 radio # was: module_callee_00499980_8e0a'),
    '0x004a0544': ('em9305_vendor_cmd', 'ble.cordio', 'MED', '# sends vendor-specific HCI command # was: ble_callee_0544'),
    '0x004a0b86': ('em9305_vendor_evt_handler', 'ble.cordio', 'MED', '# handles vendor-specific HCI events # was: ble_callee_0b86'),

    # =====================================================================
    # ble.ll (Link Layer)
    # =====================================================================
    '0x00573838': ('hciCoreLeReadFeatures', 'ble.ll', 'MED', '# reads HCI LE parameters (opcodes 0x25C,0x270,0x278) during init # was: module_callee_004CDAAC'),

    # =====================================================================
    # DM connection misc
    # =====================================================================
    '0x004b8840': ('dmConnSmGetCb', 'ble.dm_conn', 'MED', '# gets connection SM control block # was: ble_callee_8840'),
    '0x004b8b9e': ('dmConnSmResetCb', 'ble.dm_conn', 'MED', '# resets connection SM control block # was: ble_callee_8b9e'),
    '0x004b8c90': ('dmConnSmOpen', 'ble.dm_conn', 'MED', '# opens connection in SM # was: ble_callee_8c90'),
    '0x004b9474': ('dmConnSmClose', 'ble.dm_conn', 'MED', '# closes connection in SM # was: ble_callee_9474'),
    '0x004b9600': ('dmConnSmDisconnect', 'ble.dm_conn', 'MED', '# handles disconnect in SM # was: ble_callee_9600'),
    '0x004b8ab6': ('dmConnSmFindByHandle', 'ble.dm_conn', 'MED', '# finds conn SM CB by connection handle # was: module_callee_00514BAE'),

    # =====================================================================
    # Remaining misc entries
    # =====================================================================
    '0x00470ec6': ('bleParamSetDefault', 'ble.param', 'MED', '# sets default BLE parameters # was: ble.param_neighbor_00470ec6'),
    '0x004790b8': ('hciCoreResetComplete', 'ble.hci', 'MED', '# HCI reset complete handler # was: ble_neighbor_004790b8'),
    '0x004790fc': ('hciCoreResetError', 'ble.hci', 'MED', '# HCI reset error handler # was: ble_neighbor_004790fc'),
    '0x0047a4e8': ('hciCoreEvtHandlerInit', 'ble.hci', 'MED', '# initializes HCI event handler table # was: ble_neighbor_0047a4e8'),
    '0x00486570': ('bleConnHelper', 'ble.conn', 'MED', '# BLE connection helper (3/4 callers from ble) # was: ble_helper_6570'),
    '0x004e537a': ('SecAesCmac', 'ble.sec', 'MED', '# AES-CMAC: copies keys, sets event, initiates crypto # was: ble_neighbor_004e537a'),
    '0x00514b2e': ('hciCmdQueueReset', 'ble.hci', 'MED', '# resets HCI command queue # was: ble_neighbor_00514b2e'),
    '0x00515524': ('hciCmdQueueInit', 'ble.hci', 'MED', '# initializes HCI command queue # was: ble_neighbor_00515524'),
    '0x00514a96': ('hciCmdQueueAbort', 'ble.hci', 'MED', '# aborts current HCI command in queue # was: ble_neighbor_00514a96'),
    '0x00514ac8': ('hciCmdQueueFree', 'ble.hci', 'MED', '# frees HCI command queue resources # was: ble_neighbor_00514ac8'),
    '0x0056ecf4': ('em9305_phy_rssi_read', 'ble.phy', 'MED', '# reads RSSI from EM9305 PHY registers # was: ble_neighbor_0056ecf4'),
    '0x0056f3d4': ('em9305_radio_channel_map', 'ble.cordio', 'MED', '# channel map configuration for radio # was: ble_neighbor_0056f3d4'),
    '0x0056e94a': ('em9305_radio_power_ctrl', 'ble.cordio', 'MED', '# radio power control (propagated from ble) # was: ble_propagated_0056e94a'),
    '0x005d6c40': ('memValidateWrapper', 'ble', 'LOW', '# memory validation wrapper — calls validator, checks return # was: module_callee_005D6BDC'),
    '0x004ea4e0': ('bleAppSlaveInit', 'ble', 'MED', '# BLE slave application initialization # was: ble_callee_a4e0'),
    '0x00519ee8': ('hciEvtProcessLE', 'ble.hci', 'MED', '# processes LE meta event subtypes # was: ble_callee_9ee8'),
    '0x00527f22': ('hciCoreChannelFree', 'ble.hci', 'MED', '# frees LL channel resources # was: ble_callee_7f22'),
    '0x0054bade': ('em9305_phy_init_config', 'ble.phy', 'MED', '# PHY initialization configuration # was: module_callee_005156D0_bade'),
    '0x004cfc9c': ('l2cCocDataProcRsp', 'ble.l2c', 'MED', '# L2CAP CoC data response processing # was: ble_callee_fc9c'),
    '0x004d224a': ('l2cCocFlowCtrl', 'ble.l2c', 'MED', '# L2CAP CoC flow control # was: ble_callee_224a'),
    '0x004d231e': ('l2cCocCreditsUpdate', 'ble.l2c', 'MED', '# L2CAP CoC credits update # was: ble_callee_231e'),
    '0x004cdaac': ('hciCoreReadParam', 'ble.hci', 'MED', '# reads HCI parameter via LE command # was: ble_callee_daac'),
    '0x004cdbae': ('hciCoreWriteParam', 'ble.hci', 'MED', '# writes HCI parameter via LE command # was: ble_callee_dbae'),

    # =====================================================================
    # Remaining DM entries
    # =====================================================================
    '0x0049d6ac': ('dmAdvSmMsgHandler', 'ble.dm_adv', 'MED', '# DM advertising SM message handler # was: ble_callee_d6ac'),
    '0x0046c69a': ('bleMasterInit', 'ble.master', 'MED', '# BLE master role initialization # was: module_callee_004BE03A'),

    # =====================================================================
    # Misc ble entries that are HAL/driver level
    # =====================================================================
    '0x00446e88': ('nusProfileInit', 'ble', 'MED', '# initializes 0x60-byte NUS profile control block, sets timer # was: ble_callee_6e88'),
    '0x00446eb8': ('nusNotifyCback', 'ble', 'MED', '# NUS notification callback: sends event 0xC1 via msgtx # was: module_callee_0046F83C'),
    '0x00448318': ('am_hal_iom_transfer', 'ble.hal', 'MED', '# Ambiq HAL IOM blocking transfer dispatch # was: ble_callee_8318'),
    '0x00446f54': ('nusNotifyCback2', 'ble', 'MED', '# second NUS notification callback variant # was: ble_callee_6f54'),
    '0x0044830c': ('am_hal_iom_status', 'ble.hal', 'MED', '# Ambiq HAL IOM status check # was: ble_callee_830c'),
    '0x00449576': ('am_hal_gpio_config', 'ble.hal', 'MED', '# Ambiq HAL GPIO configuration # was: ble_callee_9576'),

    # =====================================================================
    # Misc connection/advertising entries
    # =====================================================================
    '0x004545b8': ('dmConnUpdInit', 'ble.dm_conn', 'MED', '# DM connection update initialization # was: ble_callee_45b8'),
    '0x004563a4': ('dmConnSmStateInit', 'ble.dm_conn', 'MED', '# DM connection SM state initialization # was: ble_callee_63a4'),
    '0x00456500': ('dmConnSmStateOpen', 'ble.dm_conn', 'MED', '# DM connection SM state: connection opened # was: ble_callee_6500'),
    '0x00456680': ('dmConnSmStateClose', 'ble.dm_conn', 'MED', '# DM connection SM state: connection closed # was: ble_callee_6680'),
    '0x00456692': ('dmConnSmStateDisc', 'ble.dm_conn', 'MED', '# DM connection SM state: disconnecting # was: ble_callee_6692'),
    '0x004563cc': ('dmConnSmSendMsg', 'ble.dm_conn', 'MED', '# sends DM conn SM internal message # was: ble_callee_63cc'),
    '0x0045654e': ('dmConnSmUpdateStart', 'ble.dm_conn', 'MED', '# starts connection parameter update # was: ble_callee_654e'),
    '0x00459214': ('bleWsfTimerInit', 'ble.wsf', 'MED', '# initializes WSF timer subsystem # was: ble_callee_9214'),
    '0x00453d56': ('dmConnCcbFind', 'ble.dm', 'MED', '# finds DM connection CCB # was: ble_callee_3d56'),

    # =====================================================================
    # Misc remaining entries (grouped by address range)
    # =====================================================================
    '0x004731e4': ('hciCoreConnCbAlloc', 'ble.hci', 'MED', '# allocates HCI connection control block # was: ble_callee_31e4'),
    '0x00477df4': ('hciCoreAclDataRx', 'ble.hci', 'MED', '# HCI ACL data receive handler # was: ble_callee_7df4'),
    '0x00478e80': ('hciCoreEvtDispatch', 'ble.hci', 'MED', '# HCI event dispatch handler # was: ble_callee_8e80'),
    '0x00478282': ('hciCoreConnParamRead', 'ble.hci', 'MED', '# reads connection parameters from HCI # was: ble_callee_8282'),
    '0x004782d4': ('hciCoreConnParamWrite', 'ble.hci', 'MED', '# writes connection parameters via HCI # was: ble_callee_82d4'),
    '0x00478fa0': ('hciCoreResetSeqWrapper', 'ble.hci', 'MED', '# wrapper for HCI reset sequence # was: ble_neighbor_004790b8_wrapper'),
    '0x00479146': ('hciCoreEvtFilter', 'ble.hci', 'MED', '# HCI event filter/routing # was: ble_callee_9146'),
    '0x0048887c': ('attsCsfConnOpen', 'ble.att', 'MED', '# ATT server CSF connection open handler # was: ble_callee_887c'),
    '0x0048b7bc': ('dmSecResolveAddr', 'ble.dm', 'MED', '# DM security address resolution # was: ble_callee_b7bc'),
    '0x00495b64': ('hciCorePhyUpdate', 'ble.hci', 'MED', '# HCI PHY update command # was: ble_callee_5b64'),
    '0x00497a3c': ('hciCoreSendExtCmd', 'ble.hci', 'MED', '# sends extended HCI command with params # was: ble_callee_7a3c'),
    '0x00497726': ('hciCorePhyConfig', 'ble.hci', 'MED', '# configures PHY parameters via HCI # was: ble_callee_9726'),
    '0x0047a430': ('hciCoreEvtMaskSet', 'ble.hci', 'MED', '# sets HCI event mask bits # was: ble_callee_a430'),
    '0x0047a4ae': ('hciCoreEvtMaskClear', 'ble.hci', 'MED', '# clears HCI event mask bits # was: ble_callee_a4ae'),
    '0x0047a582': ('hciCoreEvtMaskGet', 'ble.hci', 'MED', '# gets HCI event mask state # was: ble_callee_a582'),
    '0x00486b34': ('attsConnCbAlloc', 'ble.att', 'MED', '# allocates ATT server connection control block # was: ble_callee_6b34'),
    '0x00486c9a': ('attsConnCbFree', 'ble.att', 'MED', '# frees ATT server connection control block # was: ble_callee_6c9a'),
    # =====================================================================
    # High-address misc
    # =====================================================================
    '0x00572bfc': ('em9305_radio_aux_rx_init', 'ble.cordio', 'MED', '# pipe2 RX initialization # was: ble_callee_2bfc'),
    '0x0057302c': ('em9305_bb_isr_entry', 'ble.cordio', 'MED', '# baseband ISR entry handler # was: ble_callee_302c'),
    '0x005746d8': ('em9305_bb_scheduler_run', 'ble.cordio', 'MED', '# baseband scheduler execution # was: ble_callee_46d8'),
    '0x00572faa': ('em9305_bb_conn_handler', 'ble.cordio', 'MED', '# baseband connection event handler # was: ble_callee_2faa'),

    # =====================================================================
    # L2CAP data handling
    # =====================================================================
    '0x004d1c88': ('l2cRegister', 'ble.l2c', 'MED', '# L2CAP channel registration # was: ble_callee_1c88'),
    '0x004d1c8e': ('l2cDeregister', 'ble.l2c', 'MED', '# L2CAP channel deregistration # was: ble_callee_1c8e'),
    '0x004d1c94': ('l2cGetChannelInfo', 'ble.l2c', 'MED', '# L2CAP get channel information # was: ble_callee_1c94'),
    '0x004cd45a': ('l2cCocConnReqBuild', 'ble.l2c', 'MED', '# builds L2CAP CoC connection request # was: ble_callee_d45a'),
    '0x004cd48e': ('l2cCocConnRspBuild', 'ble.l2c', 'MED', '# builds L2CAP CoC connection response # was: ble_callee_d48e'),
    '0x004cd4c2': ('l2cCocDisconnReq', 'ble.l2c', 'MED', '# L2CAP CoC disconnect request # was: ble_callee_d4c2'),
    '0x004cd484': ('l2cCocConnRspStatus', 'ble.l2c', 'MED', '# L2CAP CoC connection response status # was: ble_callee_d484'),
    '0x004cd4a8': ('l2cCocCheckCredits', 'ble.l2c', 'MED', '# L2CAP CoC check available credits # was: ble_callee_d4a8'),
    '0x004cd4b4': ('l2cCocGetCredits', 'ble.l2c', 'MED', '# L2CAP CoC get credit count # was: ble_callee_d4b4'),
    '0x004cd93e': ('l2cCocRecvData', 'ble.l2c', 'MED', '# L2CAP CoC receive data handler # was: ble_callee_d93e'),
    '0x004cd93c': ('l2cCocRecvDataCheck', 'ble.l2c', 'MED', '# L2CAP CoC receive data check # was: ble_callee_d93c'),
    # =====================================================================
    # BLE production test
    # =====================================================================
    '0x004485e8': ('bleProductionTestInit', 'task.ble.production', 'MED', '# BLE production test initialization # was: task_ble_production_callee_85e8'),

}
