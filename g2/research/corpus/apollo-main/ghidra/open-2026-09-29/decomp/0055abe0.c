
undefined4 PB_RxHealthSingleHighlight(undefined4 param_1,byte *param_2)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  uint local_20;
  undefined4 local_1c;
  uint local_18;
  uint local_14;
  
  if (param_2 == (byte *)0x0) {
    FUN_00439c04(&local_20,DAT_0055b228,0x14);
    local_1c = CONCAT22(local_1c._2_2_,1);
    APP_errorFaultHandler(&local_20);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_1c = DAT_0055b22c;
      local_20 = 0x13b;
      FUN_0043d574(1,DAT_0055b238,DAT_0055b234,DAT_0055b230);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0055b23c);
    }
    uVar3 = 2;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_14 = (uint)*(ushort *)(param_2 + 2);
      local_18 = (uint)*param_2;
      local_1c = DAT_0055b240;
      local_20 = 0x140;
      FUN_0043d574(4,DAT_0055b238,DAT_0055b234,DAT_0055b230);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      local_20 = (uint)*(ushort *)(param_2 + 2);
      compress_log_output(0x10800000,DAT_0055b244,DAT_0055b244,*param_2);
    }
    bVar1 = FUN_00559dfc(param_2);
    if (bVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_18 = (uint)*param_2;
        local_1c = DAT_0055b250;
        local_20 = 0x149;
        FUN_0043d574(3,DAT_0055b238,DAT_0055b234,DAT_0055b230);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_0055b254,DAT_0055b254,*param_2);
      }
      uVar3 = 0;
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_18 = (uint)bVar1;
        local_1c = DAT_0055b248;
        local_20 = 0x145;
        FUN_0043d574(1,DAT_0055b238,DAT_0055b234,DAT_0055b230);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_0055b24c,DAT_0055b24c,bVar1);
      }
      uVar3 = 1;
    }
  }
  return uVar3;
}

