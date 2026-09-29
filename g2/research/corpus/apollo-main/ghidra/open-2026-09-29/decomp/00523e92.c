
void FUN_00523e92(uint param_1,undefined4 param_2)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  piVar1 = DAT_0052404c;
  iVar3 = *DAT_0052404c;
  iVar2 = *(int *)(iVar3 + 0x10);
  iVar5 = DAT_0052404c[3];
  iVar4 = DAT_0052404c[1];
  if (iVar5 < iVar2 + 2) {
    do {
      *(int *)(iVar3 + 0x10) = iVar2;
      *(undefined4 *)(iVar4 + iVar2 * 4) = 0x10000;
      iVar2 = *(int *)(iVar3 + 0x10) + 1;
      if (iVar5 <= iVar2) break;
    } while (iVar2 != 0);
    *(undefined4 *)(iVar3 + 0x10) = 0;
  }
  *(uint *)(iVar4 + *(int *)(iVar3 + 0x10) * 4) = param_1;
  iVar2 = *(int *)(iVar3 + 0x10) + 1;
  if (iVar5 <= iVar2) {
    iVar2 = 0;
  }
  *(int *)(iVar3 + 0x10) = iVar2;
  *(undefined4 *)(iVar4 + iVar2 * 4) = param_2;
  iVar2 = *(int *)(iVar3 + 0x10) + 1;
  if (iVar5 <= iVar2) {
    iVar2 = 0;
  }
  *(int *)(iVar3 + 0x10) = iVar2;
  if ((param_1 & 0xff000000) == 0) {
    return;
  }
  FUN_005140ea(iVar3);
  FUN_00514046(0xec,piVar1[2] + *(int *)(*piVar1 + 0x10) * 4 | 4);
  return;
}

