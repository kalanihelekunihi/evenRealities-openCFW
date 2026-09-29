
undefined4
FUN_00443504(undefined4 *param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  if ((param_1 == (undefined4 *)0x0) || (param_2 == (undefined4 *)0x0)) {
    uVar1 = 0xffffffff;
  }
  else if (*DAT_004437d0 == '\x01') {
    if (*DAT_0044376c == 1) {
      *param_1 = *DAT_004437d4;
      *param_2 = *DAT_00443768;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00443760,DAT_0044375c,DAT_004437dc,0x244,DAT_004437d8,*param_1,*param_2,
                     param_4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_004441e0,DAT_004441e0,*param_1,*param_2);
      }
    }
    else if (*DAT_0044376c == 2) {
      *param_1 = 0;
      *param_2 = *DAT_004437d4;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00443760,DAT_0044375c,DAT_004437dc,0x249,DAT_004437d8,*param_1,*param_2);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_004441e0,DAT_004441e0,*param_1,*param_2);
      }
    }
    else {
      *param_1 = 0;
      *param_2 = 0;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00443760,DAT_0044375c,DAT_004437dc,0x24d,DAT_004437d8,*param_1,*param_2);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_004441e0,DAT_004441e0,*param_1,*param_2);
      }
    }
    uVar1 = 0;
  }
  else {
    *param_1 = 0;
    *param_2 = 0;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00443760,DAT_0044375c,DAT_004437dc,0x253,DAT_004437d8,*param_1,*param_2);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_004441e0,DAT_004441e0,*param_1,*param_2);
    }
    uVar1 = 0;
  }
  return uVar1;
}

