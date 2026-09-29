
void am_devices_mspi_set_quad_mode
               (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 local_28 [4];
  undefined1 local_24 [8];
  undefined1 local_1c;
  undefined1 local_15;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  FUN_00439be4(local_24,param_1,0x18);
  local_1c = 0x10;
  local_24[0] = 1;
  local_15 = 1;
  iVar1 = am_devices_mspi_device_reconfigure(local_24,param_2);
  if (iVar1 == 0) {
    local_28[0] = 0x10;
    iVar1 = FUN_004c0f78(param_2,0x18,local_28);
    if (iVar1 != 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0059d174,DAT_0059d170,DAT_0059d19c,0x75,DAT_0059d1a4);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0059d1a8,DAT_0059d1a8);
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0059d174,DAT_0059d170,DAT_0059d19c,0x6f,DAT_0059d198);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0059d1a0);
    }
  }
  return;
}

