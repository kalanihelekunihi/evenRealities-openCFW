
int bq27427_write_dm_block(undefined1 *param_1)

{
  undefined1 uVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0053bb80,DAT_0053bb7c,DAT_0053c21c,0x20b,DAT_0053c218,param_1[0x23],*param_1,
                 param_1[1]);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10c00000,DAT_0053c220,DAT_0053c220,param_1[0x23],*param_1,param_1[1]);
  }
  if (param_1[0x23] == '\0') {
    iVar2 = 0;
  }
  else {
    iVar2 = bq27427_set_cfgupdate();
    if (iVar2 == 0) {
      iVar2 = bq27427_i2c_write_reg(0x61,0,1);
      if (((iVar2 == 0) && (iVar2 = bq27427_i2c_write_reg(0x3e,*param_1,1), iVar2 == 0)) &&
         (iVar2 = bq27427_i2c_write_reg(0x3f,param_1[1],1), iVar2 == 0)) {
        FUN_004910f4(1);
        iVar2 = bq27427_i2c_write_block(0x40,param_1 + 2,0x20);
        if (iVar2 == 0) {
          uVar1 = bq27427_checksum_dm_block(param_1);
          iVar2 = bq27427_i2c_write_reg(0x60,uVar1,1);
          if (iVar2 == 0) {
            FUN_004910f4(1);
            iVar2 = bq27427_soft_reset();
            if (iVar2 != 0) {
              return iVar2;
            }
            param_1[0x23] = 0;
            return 0;
          }
        }
      }
      bq27427_soft_reset();
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0053bb80,DAT_0053bb7c,DAT_0053c21c,0x236,DAT_0053c224,iVar2);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0053c228,DAT_0053c228,iVar2);
      }
    }
  }
  return iVar2;
}

