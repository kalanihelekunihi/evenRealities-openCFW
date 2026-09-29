
uint bq27427_cfgupdate_priv(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  undefined2 uVar3;
  int iVar4;
  
  if ((param_1 & 0xff) == 0) {
    uVar3 = 0x42;
  }
  else {
    uVar3 = 0x13;
  }
  iVar4 = 100;
  uVar1 = bq27427_i2c_write_reg(0,uVar3,0,param_4,param_1,param_2,param_3,param_4);
  if (uVar1 == 0) {
    do {
      FUN_004910f4(0x19);
      uVar1 = bq27427_i2c_read_reg(6,0);
      if ((int)uVar1 < 0) {
        return uVar1;
      }
    } while ((((uVar1 & 0xff) >> 4 & 1) != (param_1 & 0xff)) && (iVar4 = iVar4 + -1, iVar4 != 0));
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0053bce0,DAT_0053bcdc,DAT_0053c1f8,0x1e3,DAT_0053c1f4,param_1 & 0xff,
                   100 - iVar4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_0053c1fc,DAT_0053c1fc,param_1 & 0xff,100 - iVar4);
    }
    uVar1 = 0;
  }
  return uVar1;
}

