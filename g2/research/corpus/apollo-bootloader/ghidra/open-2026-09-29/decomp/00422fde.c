
void FUN_00422fde(int param_1)

{
  int iVar1;
  uint *puVar2;
  int iVar3;
  uint uVar4;
  
  iVar1 = DAT_00423764;
  iVar3 = *(int *)(param_1 + 0x28);
  uVar4 = (*(uint *)(DAT_00423764 + iVar3 * 0x1000 + 0x30) & 0x7fff) >> 0xe;
  if (uVar4 != 0) {
    puVar2 = (uint *)(DAT_00423764 + iVar3 * 0x1000 + 0x30);
    *puVar2 = *puVar2 & 0xffffbfff;
    puVar2 = (uint *)(iVar1 + iVar3 * 0x1000 + 0x30);
    *puVar2 = *puVar2 & 0xfffff7ff;
  }
  puVar2 = (uint *)(iVar1 + iVar3 * 0x1000 + 0x30);
  *puVar2 = *puVar2 & 0xfffffdff;
  if (*(int *)(iVar1 + iVar3 * 0x1000 + 0x18) << 0x1c < 0) {
    delay_us(DAT_00423858 / *(uint *)(param_1 + 0x30) + 1);
  }
  if (*(char *)(param_1 + 0x11b) != '\0') {
    FUN_00422d4c(param_1);
  }
  FUN_00423342(param_1);
  FUN_00422fa2(param_1);
  if (uVar4 != 0) {
    puVar2 = (uint *)(iVar1 + iVar3 * 0x1000 + 0x30);
    *puVar2 = *puVar2 | 0x4000;
  }
  puVar2 = (uint *)(iVar1 + iVar3 * 0x1000 + 0x30);
  *puVar2 = *puVar2 | 0x200;
  return;
}

