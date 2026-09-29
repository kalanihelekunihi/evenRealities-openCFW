
undefined4 isTouchNeedUpgrade(uint param_1,uint param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005610e8,DAT_005610e4,DAT_00561748,0x354,DAT_00561744,param_1,param_2);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_00560f4c;
  }
  compress_log_output(0xc800000,DAT_0056174c,DAT_0056174c,param_1,param_2);
LAB_00560f4c:
  if (param_1 == param_2) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005610e8,DAT_005610e4,DAT_00561748,0x357,DAT_00561750);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_00561754,DAT_00561754);
    }
    uVar2 = 0;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005610e8,DAT_005610e4,DAT_00561748,0x35f,DAT_00561758,param_1 >> 0x18,
                   (param_1 & 0xffffff) >> 0x10,(param_1 & 0xffff) >> 8,param_1 & 0xff,
                   param_2 >> 0x18,(param_2 & 0xffffff) >> 0x10,(param_2 & 0xffff) >> 8,
                   param_2 & 0xff);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xe000000,DAT_0056175c,DAT_0056175c,param_1 >> 0x18,
                          (param_1 & 0xffffff) >> 0x10,(param_1 & 0xffff) >> 8,param_1 & 0xff,
                          param_2 >> 0x18,(param_2 & 0xffffff) >> 0x10,(param_2 & 0xffff) >> 8,
                          param_2 & 0xff);
    }
    uVar2 = 1;
  }
  return uVar2;
}

