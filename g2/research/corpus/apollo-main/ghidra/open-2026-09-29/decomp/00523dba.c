
int FUN_00523dba(int param_1,int param_2)

{
  byte bVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  undefined4 uVar7;
  
  piVar2 = DAT_0052404c;
  uVar7 = *(undefined4 *)(param_1 + 0xc);
  if (param_2 == 0) {
    return -1;
  }
  iVar4 = *DAT_0052404c;
  iVar5 = DAT_0052404c[3];
  iVar6 = DAT_0052404c[1];
  iVar3 = *(int *)(iVar4 + 0x10);
  if (iVar5 <= iVar3 + 4) {
    do {
      *(int *)(iVar4 + 0x10) = iVar3;
      *(undefined4 *)(iVar6 + iVar3 * 4) = 0x10000;
      iVar3 = *(int *)(iVar4 + 0x10) + 1;
      if (iVar5 <= iVar3) break;
    } while (iVar3 != 0);
    *(undefined4 *)(iVar4 + 0x10) = 0;
  }
  bVar1 = *(byte *)(iVar4 + 0x10);
  while ((bVar1 & 3) != 0) {
    *(undefined4 *)(iVar6 + *(int *)(iVar4 + 0x10) * 4) = 0x10000;
    iVar3 = *(int *)(iVar4 + 0x10) + 1;
    if (iVar5 <= iVar3) {
      iVar3 = 0;
    }
    *(int *)(iVar4 + 0x10) = iVar3;
    bVar1 = *(byte *)(iVar4 + 0x10);
  }
  *(undefined4 *)(iVar6 + *(int *)(iVar4 + 0x10) * 4) = 0xf0;
  iVar3 = *(int *)(iVar4 + 0x10) + 1;
  if (iVar5 <= iVar3) {
    iVar3 = 0;
  }
  *(int *)(iVar4 + 0x10) = iVar3;
  *(undefined4 *)(iVar6 + iVar3 * 4) = uVar7;
  iVar3 = *(int *)(iVar4 + 0x10) + 1;
  if (iVar5 <= iVar3) {
    iVar3 = 0;
  }
  *(int *)(iVar4 + 0x10) = iVar3;
  *(undefined4 *)(iVar6 + iVar3 * 4) = DAT_00524058;
  iVar3 = *(int *)(iVar4 + 0x10) + 1;
  if (iVar5 <= iVar3) {
    iVar3 = 0;
  }
  *(int *)(iVar4 + 0x10) = iVar3;
  *(int *)(iVar6 + iVar3 * 4) = param_2;
  iVar3 = *(int *)(iVar4 + 0x10) + 1;
  if (iVar5 <= iVar3) {
    iVar3 = 0;
  }
  *(int *)(iVar4 + 0x10) = iVar3;
  FUN_005140ea(iVar4);
  FUN_00514046(0xec,piVar2[2] + *(int *)(*piVar2 + 0x10) * 4 | 4);
  iVar3 = *(int *)(*piVar2 + 0x14) + 1;
  if (0xffffff < iVar3) {
    iVar3 = 0;
  }
  *(int *)(*piVar2 + 0x14) = iVar3;
  return iVar3;
}

