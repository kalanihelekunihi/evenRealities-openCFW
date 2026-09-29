
void FUN_00464cba(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004651b8,DAT_004651b4,DAT_0046573c,0x85,DAT_00465738,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_00465740,DAT_00465740);
  }
  FUN_00464772(0,0,0,param_1,0x10,2,0);
  return;
}

