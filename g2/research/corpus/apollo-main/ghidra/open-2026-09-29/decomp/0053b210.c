
undefined8 bq27427_read_battery_voltage(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  
  iVar1 = bq27427_i2c_read_reg(4,0);
  if (iVar1 < 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = 0xec;
      FUN_0043d574(4,DAT_0053bb80,DAT_0053bb7c,DAT_0053bcfc,0xec,DAT_0053bcf8);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0053be90,DAT_0053be90);
    }
  }
  return CONCAT44(param_3,iVar1);
}

