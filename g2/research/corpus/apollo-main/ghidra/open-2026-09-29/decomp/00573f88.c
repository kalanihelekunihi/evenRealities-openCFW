
undefined8 pt_cmd_42_handler(int param_1,uint param_2,undefined1 *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined1 *puVar4;
  
  uVar3 = param_2;
  puVar4 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar3 = 0x9fd;
    FUN_0043d574(3,DAT_005747d4,DAT_005747d0,DAT_005747cc,0x9fd,DAT_005747c8,puVar4);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_00573fc8:
    compress_log_output(0xc000000,DAT_005747d8,DAT_005747d8);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_00573fc8;
  }
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     ((param_2 & 0xff) < 4)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = 0xa00;
      FUN_0043d574(1,DAT_005747d4,DAT_005747d0,DAT_005747cc,0xa00,DAT_00574798,DAT_005747cc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0057479c,DAT_0057479c,DAT_005747cc);
    }
    uVar2 = 0xffffffff;
    goto LAB_005741c8;
  }
  *param_3 = 0x44;
  param_3[1] = 1;
  param_3[2] = 3;
  param_3[3] = 1;
  iVar1 = productModeGet();
  if (iVar1 == 1) {
    if (*(char *)(param_1 + 4) == '\x01') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar3 = 0xa10;
        FUN_0043d574(3,DAT_005747d4,DAT_005747d0,DAT_005747cc,0xa10,DAT_005747dc);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_005747e0,DAT_005747e0);
      }
      DRV_BuzzerStart(4000,0x1e);
      param_3[4] = 0;
    }
    else if (*(char *)(param_1 + 4) == '\0') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar3 = 0xa17;
        FUN_0043d574(3,DAT_005747d4,DAT_005747d0,DAT_005747cc,0xa17,DAT_005747e4);
      }
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1f < 0) {
LAB_00574108:
        compress_log_output(0xc000000,DAT_005747e8,DAT_005747e8);
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1d < 0) goto LAB_00574108;
      }
      DRV_BuzzerStop();
      param_3[4] = 0;
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar3 = 0xa1d;
        FUN_0043d574(1,DAT_005747d4,DAT_005747d0,DAT_005747cc,0xa1d,DAT_005747ec);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_005747f0,DAT_005747f0);
      }
      param_3[4] = 1;
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = 0xa23;
      FUN_0043d574(1,DAT_005747d4,DAT_005747d0,DAT_005747cc,0xa23,DAT_005747f4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0057456c,DAT_0057456c);
    }
    param_3[4] = 5;
  }
  *param_4 = 5;
  uVar2 = 0;
LAB_005741c8:
  return CONCAT44(uVar3,uVar2);
}

