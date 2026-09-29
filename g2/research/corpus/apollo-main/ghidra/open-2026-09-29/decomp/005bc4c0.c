
undefined4 am_devices_hongshi_set_display_offset(byte param_1,byte param_2)

{
  byte bVar1;
  int iVar2;
  
  if ((*DAT_005bcf4c != '\0') && (iVar2 = FUN_0045a568(), iVar2 == 2)) {
    param_1 = param_1 + 5;
  }
  if (0x10 < param_1) {
    param_1 = 0x10;
  }
  if (0x10 < param_2) {
    param_2 = 0x10;
  }
  if (param_1 < 0x11) {
    bVar1 = am_devices_mspi_hongshi_read_bank(0xef,0);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005bc8ac,DAT_005bc8a8,DAT_005bcf54,0x214,DAT_005bcf50,bVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_005bcf58,DAT_005bcf58,bVar1);
    }
    FUN_00491102(100);
    driver_a6ng_write_register(0xef,param_1 + (bVar1 & 0xe0),0);
    FUN_00491102(100);
    driver_a6ng_write_register(0xd9,0xbf,0);
    FUN_00491102(100);
    driver_a6ng_write_register(0xd9,0xff,0);
    FUN_00491102(100);
  }
  if (param_2 < 0x11) {
    bVar1 = am_devices_mspi_hongshi_read_bank(0xf0,0);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005bc8ac,DAT_005bc8a8,DAT_005bcf54,0x221,DAT_005bcf5c,bVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_005bcf60,DAT_005bcf60,bVar1);
    }
    FUN_00491102(100);
    driver_a6ng_write_register(0xf0,param_2 + (bVar1 & 0xe0),0);
    FUN_00491102(100);
    driver_a6ng_write_register(0xd9,0xbf,0);
    FUN_00491102(100);
    driver_a6ng_write_register(0xd9,0xff,0);
    FUN_00491102(100);
  }
  FUN_004910f4(1);
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005bc8ac,DAT_005bc8a8,DAT_005bcf54,0x235,DAT_005bcf64,param_1,param_2);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc800000,DAT_005bd2b8,DAT_005bd2b8,param_1,param_2);
  }
  return 0;
}

