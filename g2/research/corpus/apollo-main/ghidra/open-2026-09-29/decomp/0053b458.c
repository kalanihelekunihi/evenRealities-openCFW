
undefined8
bq27427_unseal(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint *puVar1;
  int iVar2;
  int iVar3;
  
  puVar1 = DAT_0053bea4;
  if (*DAT_0053bea4 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x168;
      FUN_0043d574(4,DAT_0053bce0,DAT_0053bcdc,DAT_0053beac,0x168,DAT_0053bea8);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0053beb0,DAT_0053beb0);
    }
    iVar2 = -1;
  }
  else {
    iVar2 = bq27427_i2c_write_reg(0,*DAT_0053bea4 >> 0x10,0,param_4,param_2,param_3,param_4);
    if ((iVar2 == 0) && (iVar2 = bq27427_i2c_write_reg(0,(short)*puVar1,0), iVar2 == 0)) {
      iVar2 = 0;
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_2 = 0x177;
        FUN_0043d574(4,DAT_0053bce0,DAT_0053bcdc,DAT_0053beac,0x177,DAT_0053c018,iVar2);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0053c0d8,DAT_0053c0d8,iVar2);
      }
    }
  }
  return CONCAT44(param_2,iVar2);
}

