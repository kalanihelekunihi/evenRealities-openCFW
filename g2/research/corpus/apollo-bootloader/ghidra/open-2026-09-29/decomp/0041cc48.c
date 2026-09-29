
void FUN_0041cc48(int param_1)

{
  uint *puVar1;
  
  clock_request(4,0x31);
  *DAT_0041d0f8 = param_1 * 6;
  *DAT_0041d108 = *DAT_0041d108 | 0x8000;
  puVar1 = DAT_0041d0f0;
  *DAT_0041d0f0 = *DAT_0041d0f0 | 2;
  *puVar1 = *puVar1 & 0xfffffffd;
  *DAT_0041d10c = 0x40000;
  *puVar1 = *puVar1 | 1;
  return;
}

