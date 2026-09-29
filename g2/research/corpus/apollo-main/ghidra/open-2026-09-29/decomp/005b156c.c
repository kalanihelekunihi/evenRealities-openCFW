
undefined8 FUN_005b156c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  int iVar1;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  FUN_0043c0e4(DAT_005b15d8,0xac,0);
  FUN_005b3d04();
  FUN_005896b4();
  iVar1 = FUN_0043d0ce();
  uStack_10 = param_3;
  uStack_c = param_4;
  if (iVar1 << 0x1e < 0) {
    uStack_c = PTR_s_deinit_completed_005b1ac8;
    uStack_10 = 0x1b5;
    FUN_0043d574(4,DAT_005b15d0,DAT_005b15cc,PTR_s_conversate_ui_deinit_005b1acc);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__conversate_ui_deinit_completed_005b1ad0);
  }
  return CONCAT44(uStack_c,uStack_10);
}

