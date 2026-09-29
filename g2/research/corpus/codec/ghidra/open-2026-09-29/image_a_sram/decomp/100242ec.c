
undefined4 gx8002_flash_device_config(void)

{
  byte bStack_5;
  
  gx8002_flash_command_read(0x15,&bStack_5,1);
  if ((bStack_5 & 0x10) == 0) {
    bStack_5 = bStack_5 | 0x10;
    gx8002_flash_wait_ready();
    gx8002_flash_write_enable();
    gx8002_flash_command_write(0x11,&bStack_5,1);
    gx8002_flash_wait_ready();
  }
  return 0;
}

