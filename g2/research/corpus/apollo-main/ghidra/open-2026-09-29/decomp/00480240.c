
void FUN_00480240(int param_1)

{
  uint *puVar1;
  
  FUN_004c44bc(4,0x31);
  *DAT_004806d8 = param_1 * 6;
  *DAT_004806e8 = *DAT_004806e8 | 0x8000;
  puVar1 = DAT_004806d0;
  *DAT_004806d0 = *DAT_004806d0 | 2;
  *puVar1 = *puVar1 & 0xfffffffd;
  *DAT_004806ec = 0x40000;
  *puVar1 = *puVar1 | 1;
  return;
}

