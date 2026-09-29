
undefined1 gx8002_flash_read_status(void)

{
  undefined1 uStack_5;
  
  gx8002_flash_command_read(5,&uStack_5,1);
  return uStack_5;
}

