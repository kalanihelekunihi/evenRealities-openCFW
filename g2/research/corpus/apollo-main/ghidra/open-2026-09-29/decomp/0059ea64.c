
undefined8 FUN_0059ea64(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  piVar1 = DAT_0059f400;
  if (*DAT_0059f400 == 0) {
    iVar2 = osMutexNew(DAT_0059f404);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_3 = 0x4a;
        FUN_0043d574(1,DAT_0059f414,DAT_0059f410,DAT_0059f40c,0x4a,DAT_0059f408);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0059f418,DAT_0059f418);
      }
      uVar3 = 0xffffffff;
      goto LAB_0059eb0c;
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = 0x4d;
      FUN_0043d574(4,DAT_0059f414,DAT_0059f410,DAT_0059f40c,0x4d,DAT_0059f41c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0059f420,DAT_0059f420);
    }
  }
  uVar3 = 0;
LAB_0059eb0c:
  return CONCAT44(param_3,uVar3);
}

