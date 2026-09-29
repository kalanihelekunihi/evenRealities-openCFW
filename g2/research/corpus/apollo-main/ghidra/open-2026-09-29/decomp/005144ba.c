
void FUN_005144ba(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar2 = *DAT_00514b78;
  iVar1 = *(int *)(iVar2 + 4);
  if (iVar1 != 0) {
    iVar3 = *(int *)(iVar1 + 0x14);
    if (iVar3 + 2 <= *(int *)(iVar1 + 0x10)) {
      iVar4 = *(int *)(iVar1 + 8);
      *(undefined4 *)(iVar4 + iVar3 * 4) = 0x50000;
      *(undefined4 *)(iVar4 + 4 + iVar3 * 4) = 0;
      *(uint *)(iVar1 + 0x18) = *(uint *)(iVar1 + 0x18) & 0xfffffff7;
    }
    *(uint *)(iVar1 + 0x18) = *(uint *)(iVar1 + 0x18) & 0xffffffdf;
  }
  *(undefined4 *)(iVar2 + 4) = 0;
  return;
}

