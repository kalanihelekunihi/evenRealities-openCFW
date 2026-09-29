
undefined8 FUN_005b0284(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  if ((*DAT_005b09e0 != 0) && (iVar1 = osMutexRelease(*DAT_005b09e0), iVar1 != 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0x6d;
      param_2 = DAT_005b0a18;
      FUN_0043d574(1,DAT_005b09f4,DAT_005b09f0,DAT_005b0a1c,0x6d,DAT_005b0a18,iVar1,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_005b0a20,DAT_005b0a20,iVar1);
    }
  }
  return CONCAT44(param_2,param_1);
}

