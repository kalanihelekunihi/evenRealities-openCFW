
bool case_flag30_set(void)

{
  int iVar1;
  
  iVar1 = DAT_08004b68;
  *(uint *)(DAT_08004b68 + 0x14) = *(uint *)(DAT_08004b68 + 0x14) | 0x40000000;
  return -1 < *(int *)(iVar1 + 0x14) << 1;
}

