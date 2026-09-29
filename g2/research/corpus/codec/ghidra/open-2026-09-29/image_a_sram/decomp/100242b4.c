
undefined4 gx8002_flash_quad_enable(void)

{
  byte bStack_5;
  
  bStack_5 = gx8002_flash_read_status2();
  if ((bStack_5 & 2) == 0) {
    bStack_5 = bStack_5 | 2;
    gx8002_flash_wait_ready();
    gx8002_flash_write_enable();
    gx8002_flash_command_write(0x31,&bStack_5,1);
    gx8002_flash_wait_ready();
  }
  return 0;
}

