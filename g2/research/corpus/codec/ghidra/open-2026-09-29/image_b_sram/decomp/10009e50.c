
int FUN_10009e50(uint param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  
  iVar1 = DAT_10009e88;
  iVar2 = *(int *)(DAT_10009e88 + 0x18);
  iVar3 = DAT_10009e88 + 0xa0;
  *(int *)(DAT_10009e88 + 0x80) = DAT_10009e88;
  *(int *)(iVar1 + 0x90) = iVar3;
  iVar3 = 0;
  if (iVar2 != 0) {
    iVar2 = iVar2 * 0x200;
    uVar5 = iVar2 * *(int *)(iVar1 + 0x24);
    uVar4 = (uint)(*(int *)(iVar1 + 0x34) * iVar2) / uVar5;
    iVar3 = *(int *)(iVar1 + 0x48) + (param_1 - (param_1 / uVar4) * uVar4) * uVar5;
  }
  return iVar3;
}

