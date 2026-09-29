
void FUN_0041cc92(int param_1)

{
  uint *puVar1;
  
  puVar1 = DAT_0041d0f0;
  *DAT_0041d0f0 = *DAT_0041d0f0 & 0xfffffffe;
  *puVar1 = *puVar1 | 2;
  *puVar1 = *puVar1 & 0xfffffffd;
  *DAT_0041d0f8 = param_1 * 6;
  *DAT_0041d100 = 0xc0000000;
  *DAT_0041d110 = 0x40000;
  *puVar1 = *puVar1 | 1;
  return;
}

