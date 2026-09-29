
undefined4 gx8002_flash_wait_ready(void)

{
  uint uVar1;
  
  do {
    uVar1 = gx8002_flash_read_status();
  } while ((uVar1 & 1) != 0);
  return 1;
}

