
undefined4 FUN_004c0644(int param_1)

{
  uint uVar1;
  uint *puVar2;
  int iVar3;
  
  iVar3 = *(int *)(param_1 + 4);
  uVar1 = (uint)*(byte *)(param_1 + 0xb);
  if (uVar1 < 0xc) {
    puVar2 = (uint *)(DAT_004c0f5c + iVar3 * 0x1000 + 4);
    *puVar2 = *puVar2 & 0xfffffff0;
  }
  else if (uVar1 - 0xc < 2) {
    puVar2 = (uint *)(DAT_004c0f5c + iVar3 * 0x1000 + 4);
    *puVar2 = *puVar2 & 0xfffffff0 | 1;
  }
  else if (uVar1 - 0xe < 2) {
    puVar2 = (uint *)(DAT_004c0f5c + iVar3 * 0x1000 + 4);
    *puVar2 = *puVar2 & 0xfffffff0 | 3;
  }
  else if (uVar1 - 0x10 < 2) {
    puVar2 = (uint *)(DAT_004c0f5c + iVar3 * 0x1000 + 4);
    *puVar2 = *puVar2 & 0xfffffff0 | 5;
  }
  else if (uVar1 - 0x12 < 2) {
    puVar2 = (uint *)(DAT_004c0f5c + iVar3 * 0x1000 + 4);
    *puVar2 = *puVar2 & 0xfffffff0 | 7;
  }
  else if (uVar1 - 0x14 < 2) {
    puVar2 = (uint *)(DAT_004c0f5c + iVar3 * 0x1000 + 4);
    *puVar2 = *puVar2 & 0xfffffff0;
  }
  else if (uVar1 - 0x16 < 2) {
    puVar2 = (uint *)(DAT_004c0f5c + iVar3 * 0x1000 + 4);
    *puVar2 = *puVar2 & 0xfffffff0 | 9;
  }
  else if (uVar1 - 0x18 < 2) {
    puVar2 = (uint *)(DAT_004c0f5c + iVar3 * 0x1000 + 4);
    *puVar2 = *puVar2 & 0xfffffff0 | 0xb;
  }
  return 0;
}

