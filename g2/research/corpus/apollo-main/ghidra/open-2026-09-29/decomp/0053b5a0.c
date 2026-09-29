
undefined8
bq27427_read_dm_block(undefined1 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  
  param_1[0x22] = 0;
  uVar1 = bq27427_i2c_write_reg(0x3e,*param_1,1,param_4,param_2,param_3,param_4);
  if ((uVar1 == 0) && (uVar1 = bq27427_i2c_write_reg(0x3f,param_1[1],1), uVar1 == 0)) {
    FUN_004910f4(1);
    uVar1 = bq27427_i2c_read_block(0x40,param_1 + 2,0x20);
    if (uVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 0x19c;
        FUN_0043d574(4,DAT_0053bb80,DAT_0053bb7c,DAT_0053c0e4,0x19c,DAT_0053c0ec,*param_1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0053c0f0,DAT_0053c0f0,*param_1);
      }
      uVar1 = bq27427_i2c_read_reg(0x60,1);
      if (-1 < (int)uVar1) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_2 = 0x1a5;
          FUN_0043d574(4,DAT_0053bb80,DAT_0053bb7c,DAT_0053c0e4,0x1a5,DAT_0053c1c4,uVar1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_0053c1c8,DAT_0053c1c8,uVar1);
        }
        uVar3 = bq27427_checksum_dm_block(param_1);
        if ((uVar1 & 0xff) == uVar3) {
          param_1[0x22] = 1;
          param_1[0x23] = 0;
          uVar1 = 0;
          goto LAB_0053b606;
        }
        uVar1 = 0xffffffff;
      }
    }
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0x1b2;
    FUN_0043d574(4,DAT_0053bb80,DAT_0053bb7c,DAT_0053c0e4,0x1b2,DAT_0053c0e0,uVar1);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0053c0e8,DAT_0053c0e8,uVar1);
  }
LAB_0053b606:
  return CONCAT44(param_2,uVar1);
}

