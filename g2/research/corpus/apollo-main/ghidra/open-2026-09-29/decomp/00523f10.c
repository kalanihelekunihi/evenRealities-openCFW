
void FUN_00523f10(int param_1)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  
  piVar1 = DAT_0052404c;
  if (param_1 < 1) {
    return;
  }
  iVar6 = *DAT_0052404c;
  iVar8 = DAT_0052404c[3];
  iVar3 = *(int *)(iVar6 + 0x10);
  iVar7 = DAT_0052404c[1];
  if (iVar8 < iVar3 + 2) {
    do {
      *(int *)(iVar6 + 0x10) = iVar3;
      *(undefined4 *)(iVar7 + iVar3 * 4) = 0x10000;
      iVar3 = *(int *)(iVar6 + 0x10) + 1;
      if (iVar8 <= iVar3) break;
    } while (iVar3 != 0);
    *(undefined4 *)(iVar6 + 0x10) = 0;
  }
  *(undefined4 *)(iVar7 + *(int *)(iVar6 + 0x10) * 4) = 0x148;
  iVar3 = *(int *)(iVar6 + 0x10) + 1;
  if (iVar8 <= iVar3) {
    iVar3 = 0;
  }
  *(int *)(iVar6 + 0x10) = iVar3;
  *(int *)(iVar7 + iVar3 * 4) = param_1;
  iVar3 = *(int *)(iVar6 + 0x10) + 1;
  if (iVar8 <= iVar3) {
    iVar3 = 0;
  }
  if (iVar8 < iVar3 + 2) {
    do {
      *(int *)(iVar6 + 0x10) = iVar3;
      *(undefined4 *)(iVar7 + iVar3 * 4) = 0x10000;
      iVar3 = *(int *)(iVar6 + 0x10) + 1;
      if (iVar8 <= iVar3) {
        iVar3 = 0;
        goto LAB_00523f86;
      }
    } while (iVar3 != 0);
    iVar3 = 0;
  }
LAB_00523f86:
  *(int *)(iVar6 + 0x10) = iVar3;
  *(undefined4 *)(iVar7 + iVar3 * 4) = 0xf8;
  iVar3 = *(int *)(iVar6 + 0x10) + 1;
  if (iVar8 <= iVar3) {
    iVar3 = 0;
  }
  *(int *)(iVar6 + 0x10) = iVar3;
  *(undefined4 *)(iVar7 + iVar3 * 4) = 1;
  uVar4 = *(int *)(iVar6 + 0x10) + 1;
  if (iVar8 <= (int)uVar4) {
    uVar4 = 0;
  }
  if (iVar8 <= (int)(uVar4 + 4)) {
    do {
      *(uint *)(iVar6 + 0x10) = uVar4;
      *(undefined4 *)(iVar7 + uVar4 * 4) = 0x10000;
      uVar4 = *(int *)(iVar6 + 0x10) + 1;
      if (iVar8 <= (int)uVar4) goto LAB_00523fd2;
    } while (uVar4 != 0);
    uVar4 = 0;
  }
  while (uVar2 = DAT_00524050, (uVar4 & 3) != 0) {
    *(uint *)(iVar6 + 0x10) = uVar4;
    *(undefined4 *)(iVar7 + uVar4 * 4) = 0x10000;
    uVar4 = *(int *)(iVar6 + 0x10) + 1;
    if (iVar8 <= (int)uVar4) {
LAB_00523fd2:
      uVar4 = 0;
    }
  }
  iVar5 = piVar1[2];
  *(uint *)(iVar6 + 0x10) = uVar4;
  *(undefined4 *)(iVar7 + uVar4 * 4) = uVar2;
  iVar3 = *(int *)(iVar6 + 0x10) + 1;
  if (iVar8 <= iVar3) {
    iVar3 = 0;
  }
  *(int *)(iVar6 + 0x10) = iVar3;
  *(uint *)(iVar7 + iVar3 * 4) = iVar5 + (uVar4 + 4) * 4;
  iVar3 = *(int *)(iVar6 + 0x10) + 1;
  if (iVar8 <= iVar3) {
    iVar3 = 0;
  }
  *(int *)(iVar6 + 0x10) = iVar3;
  *(undefined4 *)(iVar7 + iVar3 * 4) = DAT_00524054;
  iVar3 = *(int *)(iVar6 + 0x10) + 1;
  if (iVar8 <= iVar3) {
    iVar3 = 0;
  }
  *(int *)(iVar6 + 0x10) = iVar3;
  *(int *)(iVar7 + iVar3 * 4) = piVar1[4];
  iVar3 = *(int *)(iVar6 + 0x10) + 1;
  if (iVar8 <= iVar3) {
    iVar3 = 0;
  }
  *(int *)(iVar6 + 0x10) = iVar3;
  FUN_005140ea(iVar6);
  FUN_00514046(0xec,piVar1[2] + *(int *)(*piVar1 + 0x10) * 4 | 4);
  return;
}

