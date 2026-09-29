
undefined4
PB_RxQuicklistItem(undefined4 param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_30;
  undefined4 local_2c;
  uint local_28;
  undefined4 local_24;
  undefined4 local_20;
  uint local_1c;
  uint local_18;
  undefined4 uStack_14;
  uint local_10;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (param_2 == (undefined4 *)0x0) {
    FUN_00439c04(&local_30,DAT_0055945c,0x14);
    local_2c = CONCAT22(local_2c._2_2_,1);
    APP_errorFaultHandler(&local_30);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_2c = DAT_00559460;
      local_30 = 0x99;
      FUN_0043d574(1,DAT_00559194,DAT_0055936c,DAT_00559464);
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
      local_10 = (uint)*(byte *)((int)param_2 + 0xe5);
      local_18 = param_2[4];
      uStack_14 = param_2[5];
      local_1c = (uint)*(ushort *)(param_2 + 6);
      local_20 = param_2[2];
      local_24 = param_2[1];
      local_28 = *param_2;
      local_2c = DAT_005595e8;
      local_30 = 0x9e;
      FUN_0043d574(4,DAT_00559194,DAT_0055936c,DAT_00559464);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      local_18 = (uint)*(byte *)((int)param_2 + 0xe5);
      local_20 = param_2[4];
      local_1c = param_2[5];
      local_28 = (uint)*(ushort *)(param_2 + 6);
      local_2c = param_2[2];
      local_30 = param_2[1];
      compress_log_output(0x11800000,DAT_00559778,DAT_00559778,*param_2);
    }
    uVar2 = 0;
  }
  return uVar2;
}

