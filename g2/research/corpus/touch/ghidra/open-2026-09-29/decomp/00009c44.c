
int Cy_SysClk_ImoGetFrequency(void)

{
  int iVar1;
  
  if (*(int *)(DAT_00009c74 + 0x30) < 0) {
    iVar1 = (*(uint *)(DAT_00009c74 + DAT_00009c78) & 7) * 4000000 + DAT_00009c7c;
  }
  else {
    iVar1 = 0;
  }
  return iVar1;
}

