
void FUN_0048028a(int param_1)

{
  uint *puVar1;
  
  puVar1 = DAT_004806d0;
  *DAT_004806d0 = *DAT_004806d0 & 0xfffffffe;
  *puVar1 = *puVar1 | 2;
  *puVar1 = *puVar1 & 0xfffffffd;
  *DAT_004806d8 = param_1 * 6;
  *DAT_004806e0 = 0xc0000000;
  *DAT_004806f0 = 0x40000;
  *puVar1 = *puVar1 | 1;
  return;
}

