
void NVIC_SetPriority(uint param_1,uint param_2)

{
  int iVar1;
  int iVar2;
  
  if ((int)param_1 < 0) {
    iVar2 = (((param_1 & 0xf) - 8 >> 2) + 6) * 4 + DAT_0000a270;
    iVar1 = (param_1 & 3) << 3;
    *(uint *)(iVar2 + 4) = ((param_2 & 3) << 6) << iVar1 | *(uint *)(iVar2 + 4) & ~(0xff << iVar1);
  }
  else {
    iVar2 = ((param_1 >> 2) + 0xc0) * 4;
    iVar1 = (param_1 & 3) << 3;
    *(uint *)(iVar2 + DAT_0000a26c) =
         ((param_2 & 3) << 6) << iVar1 | *(uint *)(iVar2 + DAT_0000a26c) & ~(0xff << iVar1);
  }
  return;
}

