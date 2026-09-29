
undefined8 FUN_00589b08(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  if ((*DAT_0058a30c != 0) && (iVar1 = osMutexRelease(*DAT_0058a30c), iVar1 != 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0x75;
      param_2 = DAT_0058a344;
      FUN_0043d574(1,DAT_0058a320,DAT_0058a31c,DAT_0058a348,0x75,DAT_0058a344,iVar1,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0058a34c,DAT_0058a34c,iVar1);
    }
  }
  return CONCAT44(param_2,param_1);
}

