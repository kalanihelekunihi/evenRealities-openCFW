
undefined8
am_devices_mspi_device_reconfigure
          (int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  uVar3 = param_2;
  iVar1 = FUN_004c0ea8(param_2);
  if (iVar1 == 0) {
    iVar1 = FUN_004c099c(param_2,param_1);
    if (iVar1 == 0) {
      iVar1 = FUN_004c0e1e(param_2);
      if (iVar1 == 0) {
        FUN_004c32b4(0,*(undefined1 *)(param_1 + 8));
        uVar2 = 0;
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uVar3 = 0x4d;
          FUN_0043d574(1,DAT_0059d174,DAT_0059d170,DAT_0059d16c,0x4d,DAT_0059d17c,param_4);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_0059d180,DAT_0059d180);
        }
        uVar2 = 0xffffffff;
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar3 = 0x45;
        FUN_0043d574(1,DAT_0059d174,DAT_0059d170,DAT_0059d16c,0x45,DAT_0059d17c,param_4);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0059d180,DAT_0059d180);
      }
      uVar2 = 0xffffffff;
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = 0x3d;
      FUN_0043d574(1,DAT_0059d174,DAT_0059d170,DAT_0059d16c,0x3d,DAT_0059d168,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0059d178,DAT_0059d178);
    }
    uVar2 = 0xffffffff;
  }
  return CONCAT44(uVar3,uVar2);
}

