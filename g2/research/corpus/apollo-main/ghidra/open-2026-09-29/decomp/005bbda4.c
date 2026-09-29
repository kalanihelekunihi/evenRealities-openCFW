
undefined8
am_devices_mspi_hongshi_init(char param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  undefined4 uVar1;
  uint local_10;
  
  local_10 = param_4;
  if (param_1 != '\0') {
    hongshi_power_on_sequence();
  }
  local_10 = local_10 & 0xffff0000;
  uVar1 = am_devices_mspi_hongshi_read_chipId(&local_10);
  am_devices_mspi_hongshi_configure();
  driver_a6ng_clear_framebuffer();
  if (param_1 == '\0') {
    osDelay(0x32);
    *DAT_005bcb64 = 0x4000;
  }
  else {
    FUN_004910f4(5);
    hongshi_power_off_sequence();
  }
  return CONCAT44(local_10,uVar1);
}

