
void case_configure_two_bit_field(uint param_1,uint param_2)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  uint *puVar4;
  
  iVar3 = (param_1 & 3) << 3;
  uVar2 = 0xff << iVar3;
  uVar1 = ((param_2 & 3) << 6) << iVar3;
  if (-1 < (int)param_1) {
    puVar4 = (uint *)((param_1 & 0xfffffffc) + DAT_080091e8);
    *puVar4 = *puVar4 & ~uVar2 | uVar1;
    return;
  }
  iVar3 = ((param_1 & 0xf) - 8 & 0xfffffffc) + DAT_080091ec;
  *(uint *)(iVar3 + 0x1c) = *(uint *)(iVar3 + 0x1c) & ~uVar2 | uVar1;
  return;
}

