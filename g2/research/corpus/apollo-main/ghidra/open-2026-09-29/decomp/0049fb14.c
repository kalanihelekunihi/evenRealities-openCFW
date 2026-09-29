
undefined8 _masterScan(uint param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = param_1;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_3 = param_1 & 0xff;
    uVar3 = 0x10b;
    param_2 = DAT_004a05f8;
    FUN_0043d574(4,DAT_004a02d8,DAT_004a02d4,DAT_004a05fc,0x10b,DAT_004a05f8,param_3,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004a0600,DAT_004a0600,param_1 & 0xff,uVar3,param_2,param_3);
  }
  puVar1 = DAT_004a0604;
  *DAT_004a0604 = 0;
  if ((int)(param_1 << 0x1d) < 0) {
    *puVar1 = 4;
    *(undefined1 *)(*DAT_004a0518 + 0x59) = 0;
  }
  else if ((int)(param_1 << 0x1b) < 0) {
    *(undefined1 *)(*DAT_004a0518 + 0x59) = 1;
  }
  if ((int)(param_1 << 0x1a) < 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar3 = 0x115;
      param_2 = DAT_004a0608;
      FUN_0043d574(4,DAT_004a02d8,DAT_004a02d4,DAT_004a05fc,0x115,DAT_004a0608,
                   *(undefined1 *)(*DAT_004a0518 + 0x58));
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004a060c,DAT_004a060c,*(undefined1 *)(*DAT_004a0518 + 0x58)
                         );
    }
    if (*(char *)(*DAT_004a0518 + 0x58) != '\0') {
      AppScanStop();
    }
    goto LAB_0049fcd0;
  }
  *(undefined1 *)(*DAT_004a05e8 + 0x15) = 0;
  iVar2 = FUN_004b46a8();
  if (iVar2 != 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar3 = 0x11c;
      param_2 = DAT_004a0610;
      FUN_0043d574(4,DAT_004a02d8,DAT_004a02d4,DAT_004a05fc);
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1f < 0) {
LAB_0049fc4e:
      compress_log_output(0x10000000,DAT_004a0614,DAT_004a0614);
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1d < 0) goto LAB_0049fc4e;
    }
    AppAdvStop();
  }
  if (*(char *)(*DAT_004a0518 + 0x58) == '\0') {
    *(undefined1 *)(*DAT_004a0518 + 0x58) = 1;
    AppScanStart(*(undefined1 *)(DAT_004a05e4 + 6),*(undefined1 *)(DAT_004a05e4 + 7),10000);
    goto LAB_0049fcd0;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uVar3 = 0x121;
    param_2 = DAT_004a0618;
    FUN_0043d574(4,DAT_004a02d8,DAT_004a02d4,DAT_004a05fc);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_0049fca4:
    compress_log_output(0x10000000,DAT_004a061c,DAT_004a061c);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_0049fca4;
  }
  AppScanStop();
LAB_0049fcd0:
  return CONCAT44(param_2,uVar3);
}

