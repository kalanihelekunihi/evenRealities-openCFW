
void gx8002_flash_write_protect_unlock(void)

{
  undefined1 auStack_8 [4];
  
  gx8002_flash_write_protect_set(0,auStack_8);
  return;
}

