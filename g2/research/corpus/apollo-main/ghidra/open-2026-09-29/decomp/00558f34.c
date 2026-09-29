
undefined4
PB_RxQuicklistMultItems(undefined4 param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint local_20;
  uint local_1c;
  uint local_18;
  uint local_14;
  uint local_10;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (param_2 == (byte *)0x0) {
    FUN_00439c04(&local_20,DAT_00559788,0x14);
    local_1c = CONCAT22(local_1c._2_2_,1);
    APP_errorFaultHandler(&local_20);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_1c = DAT_00559460;
      local_20 = 0xf2;
      FUN_0043d574(1,DAT_00559468,DAT_0055936c,DAT_0055978c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005595e4);
    }
    uVar2 = 2;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_10 = (uint)*(ushort *)(param_2 + 2);
      local_14 = (uint)param_2[1];
      local_18 = (uint)*param_2;
      local_1c = DAT_00559790;
      local_20 = 0xf7;
      FUN_0043d574(4,DAT_00559468,DAT_0055936c,DAT_0055978c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      local_1c = (uint)*(ushort *)(param_2 + 2);
      local_20 = (uint)param_2[1];
      compress_log_output(0x10c00000,DAT_00559794,DAT_00559794,*param_2);
    }
    uVar2 = 0;
  }
  return uVar2;
}

