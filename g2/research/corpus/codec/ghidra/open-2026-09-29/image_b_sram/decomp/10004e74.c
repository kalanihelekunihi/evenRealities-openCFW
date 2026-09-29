
void gx8002_dcache_clean_range(uint param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  
  iVar1 = DAT_10004f0c;
  uVar2 = param_1 & 0xfffffff0 | 8;
  if (0x7f < param_2) {
    uVar3 = param_2 - 0x80;
    uVar4 = uVar2;
    do {
      *(uint *)(iVar1 + 4) = uVar4;
      *(uint *)(iVar1 + 4) = uVar4 + 0x10;
      *(uint *)(iVar1 + 4) = uVar4 + 0x20;
      *(uint *)(iVar1 + 4) = uVar4 + 0x30;
      *(uint *)(iVar1 + 4) = uVar4 + 0x40;
      *(uint *)(iVar1 + 4) = uVar4 + 0x50;
      *(uint *)(iVar1 + 4) = uVar4 + 0x60;
      iVar5 = uVar4 + 0x70;
      uVar4 = uVar4 + 0x80;
      *(int *)(iVar1 + 4) = iVar5;
    } while (uVar4 != (uVar3 & 0xffffff80) + uVar2 + 0x80);
    uVar2 = uVar2 + (uVar3 & 0xffffff80) + 0x80;
    param_2 = uVar3 - (uVar3 & 0xffffff80);
  }
  iVar1 = DAT_10004f0c;
  if (0 < param_2) {
    uVar4 = uVar2;
    for (uVar3 = uVar2 + 0x10; *(uint *)(iVar1 + 4) = uVar4,
        uVar3 != (param_2 - 1U & 0xfffffff0) + uVar2 + 0x10; uVar3 = uVar3 + 0x10) {
      uVar4 = uVar3;
    }
  }
  return;
}

