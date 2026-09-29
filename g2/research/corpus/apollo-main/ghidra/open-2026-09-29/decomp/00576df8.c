
undefined4 pt_cmd_66_handler(int param_1,byte param_2,undefined1 *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  char local_1c [4];
  undefined1 *puStack_18;
  
  puStack_18 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00577358,DAT_00577354,DAT_005778cc,0xdc4,DAT_005778c8);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_00576e48;
  }
  compress_log_output(0xc000000,DAT_005778d0,DAT_005778d0);
LAB_00576e48:
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     (param_2 < 5)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00577358,DAT_00577354,DAT_005778cc,0xdc7,DAT_00577360,DAT_005778cc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00577470,DAT_00577470,DAT_005778cc);
    }
    uVar2 = 0xffffffff;
  }
  else {
    *param_3 = 0x65;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 1;
    local_1c[0] = *(char *)(param_1 + 4);
    if ((local_1c[0] == '\0') || (local_1c[0] == '\x01')) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00577358,DAT_00577354,DAT_005778cc,0xdd6,DAT_005779cc,local_1c[0]);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_005779d0,DAT_005779d0,local_1c[0]);
      }
      iVar1 = kvdbOnboardingConfigUpdateAndPersist(0,local_1c);
      if (iVar1 == 0) {
        param_3[4] = 0;
      }
      else {
        param_3[4] = 1;
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00577358,DAT_00577354,DAT_005778cc,0xde0,DAT_005779d4,local_1c[0]);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00577b7c,DAT_00577b7c,local_1c[0]);
      }
      param_3[4] = 3;
    }
    *param_4 = 5;
    uVar2 = 0;
  }
  return uVar2;
}

