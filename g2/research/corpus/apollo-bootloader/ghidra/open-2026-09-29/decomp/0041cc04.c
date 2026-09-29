
void FUN_0041cc04(void)

{
  uint *puVar1;
  
  puVar1 = DAT_0041d0f0;
  *DAT_0041d0f0 = *DAT_0041d0f0 & 0xfffffffe;
  *puVar1 = 0x110;
  *DAT_0041d0f4 = 0x100;
  *DAT_0041d0f8 = 0xffffffff;
  *DAT_0041d0fc = 0xffffffff;
  *DAT_0041d100 = 0xc0000000;
  *DAT_0041d104 = *DAT_0041d104 | 0x40000000;
  return;
}

