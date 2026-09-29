
void gx8002_flash_protection_initialize(void)

{
  undefined4 *puVar1;
  
  puVar1 = DAT_10007f9c;
  *DAT_10007f9c = DAT_10007fa0;
  puVar1[1] = 5;
  puVar1[2] = DAT_10007fa4;
  puVar1[3] = 7;
  puVar1[4] = DAT_10007fa8;
  puVar1[5] = 9;
  return;
}

