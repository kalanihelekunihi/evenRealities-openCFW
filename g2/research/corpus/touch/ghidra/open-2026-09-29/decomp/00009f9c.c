
uint Cy_SysClk_ClkHfGetFrequency(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = *(uint *)(DAT_00009fd0 + 0x28) >> 2 & 3;
  iVar1 = Cy_SysClk_ClkHfGetDivider();
  if (iVar1 == 0) {
    iVar1 = Cy_SysClk_ImoGetFrequency();
  }
  else if (iVar1 == 1) {
    iVar1 = Cy_SysClk_ExtClkGetFrequency();
  }
  else {
    iVar1 = 0;
  }
  return ((uint)(1 << uVar2) >> 1) + iVar1 >> uVar2;
}

