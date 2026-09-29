
undefined8 FUN_005b4e98(undefined4 param_1,int param_2,undefined *param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iStack_18;
  undefined *puStack_14;
  uint uStack_10;
  
  iStack_18 = param_2;
  puStack_14 = param_3;
  uStack_10 = param_4;
  if (param_2 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      puStack_14 = DAT_005b5418;
      iStack_18 = 0xed;
      FUN_0043d574(1,DAT_005b52d8,DAT_005b52d4,PTR_s_conversate_action_app_close_005b5664);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005b5420);
    }
    uVar2 = 0xffffffff;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uStack_10 = (uint)*(byte *)(param_2 + 0x90);
      puStack_14 = PTR_s_conversate_app_close__errCode____005b5668;
      iStack_18 = 0xf1;
      FUN_0043d574(3,DAT_005b52d8,DAT_005b52d4,PTR_s_conversate_action_app_close_005b5664);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__conversate_conversate_app_close_005b566c,
                          PTR_s__conversate_conversate_app_close_005b566c,
                          *(undefined1 *)(param_2 + 0x90));
    }
    FUN_0043c0e4(DAT_005b5410,6,0);
    iVar1 = FUN_0045a568();
    if (iVar1 == 1) {
      iStack_18 = *(int *)PTR_DAT_005b5670;
      puStack_14 = *(undefined **)(PTR_DAT_005b5670 + 4);
      FUN_0048eb32(DAT_005b5674,2,&iStack_18);
    }
    FUN_005b02e4(0x14,*(undefined1 *)(param_2 + 0x90));
    uVar2 = 0;
  }
  return CONCAT44(iStack_18,uVar2);
}

