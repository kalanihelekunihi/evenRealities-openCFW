
void hongshi_read_panel_mirror(void)

{
  driver_a6ng_write_register(0xd0,5,0);
  FUN_00491102(1);
  driver_a6ng_write_register(0xb,0xff,0);
  FUN_00491102(1);
  driver_a6ng_write_register(0x7e,0x88,0);
  FUN_00491102(1);
  driver_a6ng_write_register(0x7e,8,0);
  FUN_00491102(1);
  driver_a6ng_write_register(0xd2,1,0);
  FUN_00491102(1);
  driver_a6ng_write_register(0xd4,0x18,0);
  FUN_00491102(1);
  driver_a6ng_write_register(0x7d,4,0);
  FUN_00491102(100);
  driver_a6ng_write_register(0x7d,0,0);
  FUN_00491102(1);
  driver_a6ng_write_register(0xd4,0,0);
  FUN_00491102(1);
  driver_a6ng_write_register(0xb,10,0);
  FUN_00491102(1);
  am_devices_mspi_hongshi_read_bank(0xd8,0);
  return;
}

