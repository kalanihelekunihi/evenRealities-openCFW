
undefined8 FUN_0059ebc8(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  if ((*DAT_0059f400 != 0) && (iVar1 = osMutexRelease(*DAT_0059f400), iVar1 != 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0x71;
      param_2 = DAT_0059f438;
      FUN_0043d574(1,DAT_0059f414,DAT_0059f410,DAT_0059f43c,0x71,DAT_0059f438,iVar1,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0059f440,DAT_0059f440,iVar1);
    }
  }
  return CONCAT44(param_2,param_1);
}

