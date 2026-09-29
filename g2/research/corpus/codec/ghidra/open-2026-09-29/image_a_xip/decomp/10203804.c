
void gx8002_dma_clear(uint param_1)

{
  int iVar1;
  int iVar2;
  
  iVar2 = *DAT_10203824;
  iVar1 = 1 << (param_1 & 0x3f);
  *(int *)(iVar2 + 0x338) = iVar1;
  *(int *)(iVar2 + 0x340) = iVar1;
  *(int *)(iVar2 + 0x348) = iVar1;
  *(int *)(iVar2 + 0x350) = iVar1;
  *(int *)(iVar2 + 0x358) = iVar1;
  return;
}

