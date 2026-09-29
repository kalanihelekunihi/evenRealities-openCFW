
undefined8 pt_cmd_6A_handler(int param_1,uint param_2,undefined1 *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined1 *puVar4;
  
  uVar3 = param_2;
  puVar4 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar3 = 0xe14;
    FUN_0043d574(3,DAT_00577358,DAT_00577354,DAT_00577b98,0xe14,DAT_00577b94,puVar4);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_00577210:
    compress_log_output(0xc000000,DAT_00577b9c,DAT_00577b9c);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_00577210;
  }
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     ((param_2 & 0xff) < 5)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = 0xe17;
      FUN_0043d574(1,DAT_00577358,DAT_00577354,DAT_00577b98,0xe17,DAT_00577360,DAT_00577b98);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00577470,DAT_00577470,DAT_00577b98);
    }
    uVar2 = 0xffffffff;
    goto LAB_00577342;
  }
  if (*(char *)(param_1 + 4) == '\0') {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = 0xe1e;
      FUN_0043d574(3,DAT_00577358,DAT_00577354,DAT_00577b98,0xe1e,DAT_00577ba0);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1f < 0) {
LAB_005772b2:
      compress_log_output(0xc000000,DAT_00577ba4,DAT_00577ba4);
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1d < 0) goto LAB_005772b2;
    }
    FUN_005128f8();
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = 0xe24;
      FUN_0043d574(3,DAT_00577358,DAT_00577354,DAT_00577b98,0xe24,DAT_00577ba8);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1f < 0) {
LAB_005772f8:
      compress_log_output(0xc000000,DAT_00577bac,DAT_00577bac);
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1d < 0) goto LAB_005772f8;
    }
    FUN_0051299c();
  }
  *param_3 = 0x69;
  param_3[1] = 1;
  param_3[2] = 3;
  param_3[3] = 1;
  param_3[4] = 0;
  *param_4 = 5;
  uVar2 = 0;
LAB_00577342:
  return CONCAT44(uVar3,uVar2);
}

