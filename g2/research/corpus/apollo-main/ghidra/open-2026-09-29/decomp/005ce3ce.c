
undefined4 PB_RxRingEvent(undefined4 param_1,ushort *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_20;
  uint local_1c;
  uint local_18;
  undefined4 local_14;
  uint local_10;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (param_2 == (ushort *)0x0) {
    FUN_00439c04(&local_20,DAT_005ce770,0x14);
    local_1c = CONCAT22(local_1c._2_2_,1);
    APP_errorFaultHandler(&local_20);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_1c = DAT_005ce774;
      local_20 = 0x5a;
      FUN_0043d574(1,DAT_005ce73c,DAT_005ce738,DAT_005ce778);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005ce77c);
    }
    uVar2 = 2;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_10 = (uint)*param_2;
      local_14 = *(undefined4 *)(param_2 + 6);
      local_18 = (uint)(byte)param_2[4];
      local_1c = DAT_005ce780;
      local_20 = 0x5f;
      FUN_0043d574(3,DAT_005ce73c,DAT_005ce738,DAT_005ce778);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      local_1c = (uint)*param_2;
      local_20 = *(undefined4 *)(param_2 + 6);
      compress_log_output(0xcc00000,DAT_005ce784,DAT_005ce784,(char)param_2[4]);
    }
    if ((char)param_2[4] != '\x01') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_18 = (uint)(byte)param_2[4];
        local_1c = DAT_005ce788;
        local_20 = 0x79;
        FUN_0043d574(2,DAT_005ce73c,DAT_005ce738,DAT_005ce778);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_005ce78c,DAT_005ce78c,(char)param_2[4]);
      }
    }
    uVar2 = 0;
  }
  return uVar2;
}

