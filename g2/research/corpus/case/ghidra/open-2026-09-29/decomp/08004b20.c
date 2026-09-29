
bool case_flag31_set(void)

{
  int iVar1;
  
  iVar1 = DAT_08004b38;
  *(uint *)(DAT_08004b38 + 0x14) = *(uint *)(DAT_08004b38 + 0x14) | 0x80000000;
  return -1 < *(int *)(iVar1 + 0x14);
}

