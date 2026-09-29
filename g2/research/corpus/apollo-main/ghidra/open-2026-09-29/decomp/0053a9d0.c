
uint bq25180_read_device_id
               (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = bq25180_read_register(0xc);
  if ((int)uVar1 < 1) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0053af78,DAT_0053af60,DAT_0053af74,0xe4,DAT_0053af70,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0053af7c,DAT_0053af7c);
    }
    uVar1 = 0xffffffff;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0053af78,DAT_0053af60,DAT_0053af74,0xe8,DAT_0053af80,uVar1,uVar1 & 0xf);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_0053af84,DAT_0053af84,uVar1,uVar1 & 0xf);
    }
    uVar1 = uVar1 & 0xf;
  }
  return uVar1;
}

