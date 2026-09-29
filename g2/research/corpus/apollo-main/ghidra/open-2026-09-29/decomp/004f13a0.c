
undefined8 FUN_004f13a0(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

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
    uStack_14 = DAT_004f1a68;
    uStack_18 = 0x326;
    FUN_0043d574(3,DAT_004f18a0,DAT_004f189c,DAT_004f1a6c);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_004f1a70,DAT_004f1a70);
  }
  piVar1 = DAT_004f1a74;
  if (*DAT_004f1a74 != 0) {
    FUN_0044d7b8(*DAT_004f1a74);
    *piVar1 = 0;
  }
  *DAT_004f1a78 = 0;
  *DAT_004f1a7c = 0;
  *DAT_004f1a80 = 0;
  *DAT_004f1a84 = 0;
  *DAT_004f1a88 = 0;
  *DAT_004f1a8c = 0;
  *DAT_004f1a90 = 0;
  *DAT_004f1a94 = 0;
  if (*DAT_004f1a20 != 0) {
    FUN_0043dfa4(*DAT_004f1a20,1);
  }
  *DAT_004f1a5c = 0;
  *DAT_004f19f8 = 0;
  *DAT_004f1a60 = 0;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uStack_10 = *DAT_004f19e8;
    uStack_14 = DAT_004f1a98;
    uStack_18 = 0x33f;
    FUN_0043d574(3,DAT_004f18a0,DAT_004f189c,DAT_004f1a6c);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc400000,DAT_004f1a9c,DAT_004f1a9c,*DAT_004f19e8);
  }
  piVar1 = DAT_004f19fc;
  if ((*DAT_004f19fc != 0) && (iVar2 = ui_common_api_fn_00509dfa(*DAT_004f19fc), iVar2 == 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uStack_14 = DAT_004f1a00;
      uStack_18 = 0x342;
      FUN_0043d574(4,DAT_004f18a0,DAT_004f189c,DAT_004f1a6c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004f1a04,DAT_004f1a04);
    }
    FUN_0043c0e4(&uStack_18,10,0);
    FUN_0043c0e4(&uStack_18,10,0);
    ui_common_api_fn_00509e14(*piVar1,&uStack_18,6);
    FUN_004f3440(&uStack_18,6);
  }
  return CONCAT44(uStack_14,uStack_18);
}

