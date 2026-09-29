
undefined4 FUN_004ece5c(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  if ((param_1 == 0) || (param_2 == 0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004ed6e4,DAT_004ed04c,DAT_004ed700,0x6ad,DAT_004ed6fc,param_1,param_2,
                   param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_004ed704,DAT_004ed704,param_1,param_2);
    }
    uVar2 = 0;
  }
  else {
    uVar2 = 1;
  }
  return uVar2;
}

