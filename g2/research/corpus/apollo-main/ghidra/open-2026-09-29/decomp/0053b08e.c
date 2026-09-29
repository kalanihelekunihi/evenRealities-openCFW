
undefined4
bq27427_i2c_write_block(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined1 local_34;
  undefined1 auStack_33 [35];
  undefined4 uStack_10;
  
  local_34 = param_1;
  uStack_10 = param_4;
  FUN_00439be4(auStack_33,param_2,param_3);
  iVar1 = hal_i2c_transfer_joined(7,0x55,&local_34,1,auStack_33,param_3);
  if (iVar1 != 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0053bce0,DAT_0053bcdc,DAT_0053bb70,0xb5,DAT_0053bb6c,iVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0053bce4,DAT_0053bce4,iVar1);
    }
  }
  return 0;
}

