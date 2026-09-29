
undefined8 pt_cmd_22_handler(int param_1,uint param_2,undefined1 *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  char *pcVar3;
  uint uVar4;
  undefined1 *puVar5;
  
  uVar4 = param_2;
  puVar5 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar4 = 0x6ee;
    FUN_0043d574(3,DAT_00571fd8,DAT_00571fd4,DAT_00572934,0x6ee,DAT_00572930,puVar5);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_00571e8e;
  }
  compress_log_output(0xc000000,DAT_00572938,DAT_00572938);
LAB_00571e8e:
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     ((param_2 & 0xff) < 4)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar4 = 0x6f1;
      FUN_0043d574(1,DAT_00571fd8,DAT_00571fd4,DAT_00572934,0x6f1,DAT_005726ec,DAT_00572934);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00572850,DAT_00572850,DAT_00572934);
    }
    uVar2 = 0xffffffff;
  }
  else {
    *param_3 = 0x26;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 1;
    iVar1 = productModeGet();
    if (iVar1 == 1) {
      pcVar3 = (char *)FUN_0044347a();
      if ((pcVar3 != (char *)0x0) && (*pcVar3 == '\x01')) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uVar4 = 0x701;
          FUN_0043d574(3,DAT_00571fd8,DAT_00571fd4,DAT_00572934,0x701,DAT_00572a2c);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_00572a30,DAT_00572a30);
        }
        FUN_004443cc(0x10b,0,0);
      }
      param_3[4] = 0;
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar4 = 0x708;
        FUN_0043d574(1,DAT_00571fd8,DAT_00571fd4,DAT_00572934,0x708,DAT_00572854);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00572ad8,DAT_00572ad8);
      }
      param_3[4] = 5;
    }
    *param_4 = 5;
    uVar2 = 0;
  }
  return CONCAT44(uVar4,uVar2);
}

