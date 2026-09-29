
undefined4
am_devices_jbd4010_set_mode(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 auStack_24 [20];
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  FUN_0043c0e4(auStack_24,0x14,0);
  if (((param_1 == 'q') || (param_1 == 'r')) || (param_1 == 's')) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00593900,DAT_005938fc,PTR_s_am_devices_jbd4010_set_mode_00593990,0x342,
                   PTR_s_jbd4010_set_mode___0x_02x_0059398c,param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,PTR_s__driver_jbd4010_jbd4010_set_mode_00593994,
                          PTR_s__driver_jbd4010_jbd4010_set_mode_00593994,param_1);
    }
    jbd4010_write_command(param_1,auStack_24,0);
    FUN_00491102(2);
    jbd4010_write_command(0x97,auStack_24,0);
    FUN_00491102(2000);
    am_devices_jbd4010_QSPI_PartialReflash_async(0,0,0,0,0x280,0x1e0);
  }
  else {
    if (param_1 != 't') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00593900,DAT_005938fc,PTR_s_am_devices_jbd4010_set_mode_00593990,0x353,
                     PTR_s_jbd4010_set_mode_failed__mode___0_00593998,param_1);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__driver_jbd4010_jbd4010_set_mode_0059399c,
                            PTR_s__driver_jbd4010_jbd4010_set_mode_0059399c,param_1);
      }
      return 0xffffffff;
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00593900,DAT_005938fc,PTR_s_am_devices_jbd4010_set_mode_00593990,0x34a,
                   PTR_s_jbd4010_set_mode___0x_02x_0059398c,0x74);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,PTR_s__driver_jbd4010_jbd4010_set_mode_00593994,
                          PTR_s__driver_jbd4010_jbd4010_set_mode_00593994,0x74);
    }
    jbd4010_write_command(0x71,auStack_24,0);
    FUN_00491102(2);
    jbd4010_write_command(0x73,auStack_24,0);
    FUN_00491102(2);
    jbd4010_write_command(0x97,auStack_24,0);
    FUN_00491102(2000);
  }
  return 0;
}

