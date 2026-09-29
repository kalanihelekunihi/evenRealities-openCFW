
undefined4 FUN_005b01ca(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  
  piVar1 = DAT_005b09e0;
  if ((*DAT_005b09e0 == 0) && (iVar2 = FUN_005b0120(), iVar2 != 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005b09f4,DAT_005b09f0,DAT_005b0a08,0x58,DAT_005b0a04,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005b0a0c,DAT_005b0a0c);
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
        FUN_0043d574(1,DAT_005b09f4,DAT_005b09f0,DAT_005b0a08,0x5f,DAT_005b0a10,iVar2,param_4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_005b0a14,DAT_005b0a14,iVar2);
      }
      uVar3 = 0;
    }
  }
  return uVar3;
}

