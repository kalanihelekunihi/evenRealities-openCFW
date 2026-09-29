
undefined8
am_devices_mspi_set_serail_mode
          (undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_18;
  undefined4 local_14;
  uint local_10;
  undefined4 uStack_c;
  
  local_10 = param_3;
  uStack_c = param_4;
  iVar1 = am_devices_mspi_device_reconfigure(param_1,param_2);
  local_18 = param_1;
  local_14 = param_2;
  if (iVar1 == 0) {
    local_10 = local_10 & 0xffffff00;
    iVar1 = FUN_004c0f78(param_2,0x18,&local_10);
    if (iVar1 != 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_14 = DAT_0059d190;
        local_18 = 0x60;
        FUN_0043d574(1,DAT_0059d174,DAT_0059d170,DAT_0059d188);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0059d194);
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_14 = DAT_0059d184;
      local_18 = 0x5a;
      FUN_0043d574(1,DAT_0059d174,DAT_0059d170,DAT_0059d188);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0059d18c);
    }
  }
  return CONCAT44(local_14,local_18);
}

