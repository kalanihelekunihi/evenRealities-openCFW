
void touch_sub_2b64(int param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  uint *puVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  iVar6 = *(int *)(param_2 + 0xc) + param_1 * 0x90;
  iVar5 = *(int *)(param_2 + 0x10) + param_1 * 0x3c;
  iVar2 = *(int *)(param_2 + 0x28) + 0x10;
  if (*(char *)(iVar6 + 0x7b) == '\a') {
    iVar2 = *(int *)(param_2 + 0x2c) + 0x24;
    iVar7 = 0xb;
  }
  else {
    iVar7 = 7;
  }
  puVar3 = (uint *)(iVar2 + iVar7 * (uint)*(ushort *)(iVar6 + 0x80) * 4);
  for (uVar1 = 0; uVar1 < *(ushort *)(iVar6 + 0x38); uVar1 = uVar1 + 1) {
    uVar4 = *puVar3 & DAT_00005ec8;
    *puVar3 = uVar4;
    uVar4 = uVar4 | *(byte *)(iVar5 + 0x2e);
    *puVar3 = uVar4;
    *puVar3 = uVar4 | (uint)*(byte *)(iVar5 + 0x30) << 0x10;
    puVar3 = puVar3 + iVar7;
  }
  return;
}

