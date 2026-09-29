
undefined4 FUN_004722d8(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 local_110;
  undefined1 local_10f;
  undefined1 local_10e;
  undefined1 local_10d;
  undefined1 local_10c;
  undefined1 local_10b;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  FUN_0043c0e4(&local_110,0xfe,0);
  local_110 = 0;
  local_10f = 0x1a;
  local_10e = 0x8a;
  local_10d = 1;
  local_10c = (undefined1)param_1;
  local_10b = (undefined1)((uint)param_1 >> 8);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00472bbc,DAT_00472bb8,PTR_s_RING_TouchAlgoReportTimeProcess_00472bcc,0x138,
                 PTR_s_RING_TouchAlgoReportTime_send_00472bc8);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__ring_proto_RING_TouchAlgoReport_00472bd0,
                        PTR_s__ring_proto_RING_TouchAlgoReport_00472bd0);
  }
  APP_BleRingSendDataMsg(&local_110,6);
  return 0;
}

