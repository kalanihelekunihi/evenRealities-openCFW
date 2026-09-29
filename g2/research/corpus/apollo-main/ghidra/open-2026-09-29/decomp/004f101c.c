
undefined8 FUN_004f101c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uStack_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  
  uStack_18 = param_2;
  uStack_14 = param_3;
  uStack_10 = param_4;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uStack_14 = DAT_004f1a08;
    uStack_18 = 0x2a5;
    FUN_0043d574(4,DAT_004f18a0,DAT_004f189c,DAT_004f1a0c);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004f1a10,DAT_004f1a10);
  }
  *DAT_004f19f8 = 0;
  piVar1 = DAT_004f19fc;
  if ((*DAT_004f19fc != 0) && (iVar2 = ui_common_api_fn_00509dfa(*DAT_004f19fc), iVar2 == 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uStack_14 = DAT_004f1a00;
      uStack_18 = 0x2a8;
      FUN_0043d574(4,DAT_004f18a0,DAT_004f189c,DAT_004f1a0c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004f1a04);
    }
    FUN_0043c0e4(&uStack_18,10,0);
    FUN_0043c0e4(&uStack_18,10,0);
    ui_common_api_fn_00509e14(*piVar1,&uStack_18,6);
    FUN_004f3440(&uStack_18,6);
  }
  return CONCAT44(uStack_14,uStack_18);
}

