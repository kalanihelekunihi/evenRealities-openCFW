
int bq27427_read_charge(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar1 = bq27427_i2c_read_reg(param_1,0);
  if (iVar1 < 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0053bb80,DAT_0053bb7c,DAT_0053bd04,0xf9,DAT_0053bd00,param_1,iVar1,param_4)
      ;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_0053be94,DAT_0053be94,param_1,iVar1);
    }
  }
  return iVar1;
}

