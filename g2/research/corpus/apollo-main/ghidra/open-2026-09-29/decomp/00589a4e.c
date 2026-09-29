
undefined4 FUN_00589a4e(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  
  piVar1 = DAT_0058a30c;
  if ((*DAT_0058a30c == 0) && (iVar2 = FUN_005899a4(), iVar2 != 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0058a320,DAT_0058a31c,DAT_0058a334,0x60,DAT_0058a330,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0058a338,DAT_0058a338);
    }
    uVar3 = 0;
  }
  else {
    iVar2 = osMutexAcquire(*piVar1,0xffffffff);
    if (iVar2 == 0) {
      uVar3 = 1;
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0058a320,DAT_0058a31c,DAT_0058a334,0x67,DAT_0058a33c,iVar2,param_4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_0058a340,DAT_0058a340,iVar2);
      }
      uVar3 = 0;
    }
  }
  return uVar3;
}

