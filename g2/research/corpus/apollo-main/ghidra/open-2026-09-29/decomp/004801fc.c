
void FUN_004801fc(void)

{
  uint *puVar1;
  
  puVar1 = DAT_004806d0;
  *DAT_004806d0 = *DAT_004806d0 & 0xfffffffe;
  *puVar1 = 0x110;
  *DAT_004806d4 = 0x100;
  *DAT_004806d8 = 0xffffffff;
  *DAT_004806dc = 0xffffffff;
  *DAT_004806e0 = 0xc0000000;
  *DAT_004806e4 = *DAT_004806e4 | 0x40000000;
  return;
}

