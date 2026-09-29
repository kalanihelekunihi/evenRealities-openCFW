
void FUN_004b1548(void)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  
  iVar3 = *DAT_004b178c;
  iVar2 = *(int *)(iVar3 + 0x28);
  uVar1 = *(uint *)(iVar3 + 0x24);
  uVar4 = *(int *)(iVar3 + 0x2c) + uVar1;
  iVar3 = *(int *)(iVar3 + 0x30) + iVar2;
  if ((int)uVar1 < 0) {
    uVar1 = 0;
  }
  if (iVar2 < 0) {
    iVar2 = 0;
  }
  FUN_00514846(0x110,uVar1 & 0xffff | iVar2 << 0x10);
  FUN_00514846(0x114,uVar4 & 0xffff | iVar3 * 0x10000);
  return;
}

