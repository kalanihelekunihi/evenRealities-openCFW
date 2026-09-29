
undefined4
uled_driver_identify(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  int *piVar4;
  uint uVar5;
  
  piVar1 = DAT_004ca680;
  piVar4 = DAT_004ca67c;
  if ((DAT_004ca67c == (int *)0x0) || (DAT_004ca680 == (int *)0x0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004ca674,DAT_004ca670,DAT_004ca688,0x61,DAT_004ca684,piVar4,piVar1,param_4)
      ;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_004ca68c,DAT_004ca68c,piVar4,piVar1);
    }
  }
  else if (DAT_004ca67c < DAT_004ca680) {
    uVar3 = (int)DAT_004ca680 - (int)DAT_004ca67c >> 2;
    if (3 < uVar3) {
      uVar3 = 3;
    }
    for (uVar5 = 0; (uVar5 < uVar3 && (piVar4 = DAT_004ca67c + uVar5, piVar4 < DAT_004ca680));
        uVar5 = uVar5 + 1) {
      if ((*piVar4 != 0) && (*(char *)(*piVar4 + 0x3c) == param_1)) {
        *DAT_004ca664 = *piVar4;
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004ca674,DAT_004ca670,DAT_004ca688,0x76,DAT_004ca6a0,param_1,uVar5);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc800000,DAT_004ca6a4,DAT_004ca6a4,param_1,uVar5);
        }
        return 0;
      }
    }
    osDelay(1);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004ca674,DAT_004ca670,DAT_004ca688,0x7c,DAT_004ca698);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ca69c,DAT_004ca69c);
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004ca674,DAT_004ca670,DAT_004ca688,0x66,DAT_004ca690,piVar4,piVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_004ca694,DAT_004ca694,piVar4,piVar1);
    }
  }
  return 0xffffffff;
}

