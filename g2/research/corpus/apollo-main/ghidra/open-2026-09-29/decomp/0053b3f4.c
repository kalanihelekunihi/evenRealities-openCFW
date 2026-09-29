
int bq27427_seal(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar1 = bq27427_i2c_write_reg(0,0x20,0,param_4,param_1,param_2,param_3,param_4);
  if (iVar1 == 0) {
    iVar1 = 0;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0053bce0,DAT_0053bcdc,DAT_0053bea0,0x15c,DAT_0053be9c,iVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0053c0d4,DAT_0053c0d4,iVar1);
    }
  }
  return iVar1;
}

