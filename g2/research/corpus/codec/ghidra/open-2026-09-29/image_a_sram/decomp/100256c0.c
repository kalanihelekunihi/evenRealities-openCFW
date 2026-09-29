
void gx_dcache_clean_invalid_range(uint param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  iVar3 = iRam10025718;
  uVar2 = param_1 & 0xfffffff0 | 10;
  for (; iVar1 = iRam10025718, 0x7f < param_2; param_2 = param_2 + -0x80) {
    *(uint *)(iVar3 + 4) = uVar2;
    *(uint *)(iVar3 + 4) = uVar2 + 0x10;
    *(uint *)(iVar3 + 4) = uVar2 + 0x20;
    *(uint *)(iVar3 + 4) = uVar2 + 0x30;
    *(uint *)(iVar3 + 4) = uVar2 + 0x40;
    *(uint *)(iVar3 + 4) = uVar2 + 0x50;
    *(uint *)(iVar3 + 4) = uVar2 + 0x60;
    *(uint *)(iVar3 + 4) = uVar2 + 0x70;
    uVar2 = uVar2 + 0x80;
  }
  iVar3 = uVar2 + param_2;
  for (; 0 < param_2; param_2 = param_2 + -0x10) {
    *(int *)(iVar1 + 4) = iVar3 - param_2;
  }
  return;
}

