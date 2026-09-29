
void FUN_00422d4c(int param_1)

{
  int iVar1;
  int iVar2;
  uint *puVar3;
  
  iVar1 = DAT_00423764;
  iVar2 = *(int *)(param_1 + 0x28);
  *(undefined4 *)(DAT_00423764 + iVar2 * 0x1000 + 0x48) = 0;
  puVar3 = (uint *)(iVar1 + iVar2 * 0x1000 + 4);
  *puVar3 = *puVar3 & 0xffffffdf;
  puVar3 = (uint *)(iVar1 + iVar2 * 0x1000 + 0x50);
  *puVar3 = *puVar3 & 0xfffff000;
  return;
}

