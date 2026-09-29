
void am_device_mspi_hongshi_read_sn(void)

{
  int iVar1;
  undefined4 in_r3;
  int iVar2;
  undefined1 local_24 [20];
  undefined4 uStack_10;
  
  uStack_10 = in_r3;
  driver_a6ng_write_register(0x65,0,0);
  driver_a6ng_write_register(0x66,2,0);
  driver_a6ng_write_register(0x67,0,0);
  driver_a6ng_write_register(100,0x85,0);
  FUN_004910f4(1);
  local_24[0] = am_devices_mspi_hongshi_read_bank(0x6c,0);
  local_24[1] = am_devices_mspi_hongshi_read_bank(0x6d,0);
  local_24[2] = am_devices_mspi_hongshi_read_bank(0x6e,0);
  local_24[3] = am_devices_mspi_hongshi_read_bank(0x6f,0);
  driver_a6ng_write_register(100,0,0);
  FUN_004910f4(1);
  driver_a6ng_write_register(0x65,0,0);
  driver_a6ng_write_register(0x66,2,0);
  driver_a6ng_write_register(0x67,1,0);
  driver_a6ng_write_register(100,0x85,0);
  FUN_004910f4(1);
  local_24[4] = am_devices_mspi_hongshi_read_bank(0x6c,0);
  local_24[5] = am_devices_mspi_hongshi_read_bank(0x6d,0);
  local_24[6] = am_devices_mspi_hongshi_read_bank(0x6e,0);
  local_24[7] = am_devices_mspi_hongshi_read_bank(0x6f,0);
  driver_a6ng_write_register(100,0,0);
  FUN_004910f4(1);
  driver_a6ng_write_register(0x65,0,0);
  driver_a6ng_write_register(0x66,2,0);
  driver_a6ng_write_register(0x67,2,0);
  driver_a6ng_write_register(100,0x85,0);
  FUN_004910f4(1);
  local_24[8] = am_devices_mspi_hongshi_read_bank(0x6c,0);
  local_24[9] = am_devices_mspi_hongshi_read_bank(0x6d,0);
  local_24[10] = am_devices_mspi_hongshi_read_bank(0x6e,0);
  local_24[0xb] = am_devices_mspi_hongshi_read_bank(0x6f,0);
  driver_a6ng_write_register(100,0,0);
  FUN_004910f4(1);
  driver_a6ng_write_register(0x65,0,0);
  driver_a6ng_write_register(0x66,2,0);
  driver_a6ng_write_register(0x67,3,0);
  driver_a6ng_write_register(100,0x85,0);
  FUN_004910f4(1);
  local_24[0xc] = am_devices_mspi_hongshi_read_bank(0x6c,0);
  local_24[0xd] = am_devices_mspi_hongshi_read_bank(0x6d,0);
  local_24[0xe] = am_devices_mspi_hongshi_read_bank(0x6e,0);
  local_24[0xf] = am_devices_mspi_hongshi_read_bank(0x6f,0);
  driver_a6ng_write_register(100,0,0);
  FUN_004910f4(1);
  driver_a6ng_write_register(0x65,1,0);
  driver_a6ng_write_register(0x66,2,0);
  driver_a6ng_write_register(0x67,0,0);
  driver_a6ng_write_register(100,0x85,0);
  FUN_004910f4(1);
  local_24[0x10] = am_devices_mspi_hongshi_read_bank(0x6c,0);
  local_24[0x11] = am_devices_mspi_hongshi_read_bank(0x6d,0);
  local_24[0x12] = am_devices_mspi_hongshi_read_bank(0x6e,0);
  driver_a6ng_write_register(100,0,0);
  FUN_004910f4(1);
  iVar2 = 0;
  do {
    if (0x12 < iVar2) {
      return;
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005bd2f4,DAT_005bd2f0,DAT_005bd2ec,0x2d3,DAT_005bd2e8,local_24[iVar2]);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1f < 0) {
LAB_005bcb0a:
      compress_log_output(0xc400000,DAT_005bd2f8,DAT_005bd2f8,local_24[iVar2]);
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1d < 0) goto LAB_005bcb0a;
    }
    iVar2 = iVar2 + 1;
  } while( true );
}

