
int bq27427_change_chemistry_profile
              (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar1 = bq27427_unseal();
  if (iVar1 < 0) {
    return -1;
  }
  bq27427_i2c_write_reg(0,8,0);
  iVar1 = bq27427_i2c_read_reg(0,0);
  if (iVar1 < 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0053c238,DAT_0053c234,DAT_0053c230,0x271,DAT_0053c22c,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0053c23c,DAT_0053c23c);
    }
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0053c238,DAT_0053c234,DAT_0053c230,0x272,DAT_0053c240,iVar1);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0053c244,DAT_0053c244,iVar1);
  }
  iVar1 = bq27427_set_cfgupdate();
  if (iVar1 == 0) {
    bq27427_execute_control_word(0x31);
    FUN_004910f4(1);
    iVar1 = bq27427_soft_reset();
    if (iVar1 == 0) {
      bq27427_i2c_write_reg(0,8,0);
      iVar1 = bq27427_i2c_read_reg(0,0);
      if (iVar1 < 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0053c238,DAT_0053c234,DAT_0053c230,0x281,DAT_0053c22c);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_0053c23c,DAT_0053c23c);
        }
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0053c238,DAT_0053c234,DAT_0053c230,0x282,DAT_0053c248,iVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0053c24c,DAT_0053c24c,iVar1);
      }
      bq27427_seal();
      return 0;
    }
    return iVar1;
  }
  return iVar1;
}

