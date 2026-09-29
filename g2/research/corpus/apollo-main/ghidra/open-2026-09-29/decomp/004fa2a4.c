
void FUN_004fa2a4(undefined4 param_1,undefined4 param_2,undefined1 param_3,undefined4 param_4)

{
  int iVar1;
  
  FUN_0044ea04(*DAT_004fac60,param_1,0);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004fa710,DAT_004fa400,DAT_004fac6c,0x109b,DAT_004fac68,param_1,param_1,
                 param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10c00000,DAT_004faf88,DAT_004faf88,param_1,param_1,param_3);
  }
  return;
}

