
undefined1 gx8002_flash_read_status2(void)

{
  undefined1 uStack_5;
  
  gx8002_flash_command_read(0x35,&uStack_5,1);
  return uStack_5;
}

