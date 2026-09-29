
undefined4 gx8002_flash_quad_enable_pair(void)

{
  undefined1 local_8;
  byte bStack_7;
  
  local_8 = gx8002_flash_read_status();
  bStack_7 = gx8002_flash_read_status2();
  if ((bStack_7 & 2) == 0) {
    bStack_7 = bStack_7 | 2;
    gx8002_flash_wait_ready();
    gx8002_flash_write_enable();
    gx8002_flash_command_write(1,&local_8,2);
    gx8002_flash_wait_ready();
  }
  return 0;
}

