
undefined4 FUN_00472244(void)

{
  int iVar1;
  undefined1 local_108;
  undefined1 local_107;
  undefined1 local_106;
  undefined1 local_105;
  
  FUN_0043c0e4(&local_108,0xfe,0);
  local_108 = 0;
  local_107 = 0x1a;
  local_106 = 0x94;
  local_105 = 1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00472bbc,DAT_00472bb8,DAT_00472bb4,0x120,DAT_00472bb0);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_00472bc0);
  }
  FUN_0043dacc(PTR_s_ring_heart_00472bc4,0x10,&local_108,4);
  APP_BleRingSendDataMsg(&local_108,4);
  return 0;
}

