
uint * FUN_100070ac(int *param_1,int param_2)

{
  int *piVar1;
  uint *puVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  uint *puVar6;
  uint uVar7;
  uint uVar8;
  int iVar9;
  uint *puVar10;
  
  uVar7 = param_2 + 0xfU & 0xfffffff0;
  if ((uint)(*param_1 - param_1[2]) < uVar7) {
    return (uint *)0x0;
  }
  if (uVar7 < 0x4001) {
    uVar8 = param_2 + 0xfU >> 4;
  }
  else if ((int)uVar7 < 0) {
    uVar8 = 0x412;
  }
  else {
    iVar9 = 0x1f;
    uVar8 = uVar7;
    do {
      iVar5 = iVar9;
      uVar8 = uVar8 * 2;
      iVar9 = iVar5 + -1;
    } while (-1 < (int)uVar8);
    uVar8 = iVar5 + 0x3f2;
    if (0x412 < uVar8) {
      return (uint *)0x0;
    }
  }
  puVar10 = (uint *)(param_1 + uVar8 * 5 + 6);
LAB_100070d6:
  puVar6 = (uint *)puVar10[1];
  while( true ) {
    if (puVar6 == puVar10) goto LAB_1000720e;
    uVar3 = *puVar6;
    if (uVar7 <= uVar3) break;
    puVar6 = (uint *)puVar6[1];
  }
  uVar4 = uVar3 - uVar7;
  iVar9 = *(int *)((int)puVar6 + uVar3 + 0xc);
  piVar1 = (int *)puVar6[1];
  *(int **)(iVar9 + 4) = piVar1;
  *(int *)((int)piVar1 + *piVar1 + 0xc) = iVar9;
  puVar6[1] = 0;
  param_1[uVar8 * 5 + 10] = param_1[uVar8 * 5 + 10] + -1;
  if ((uVar4 < 0x4011) && (uVar4 < uVar7 + 0x10)) goto LAB_100071d4;
  puVar10 = (uint *)((int)puVar6 + uVar7 + 8);
  uVar8 = uVar4 - 0x10;
  iVar9 = param_1[2];
  *puVar6 = uVar7;
  *puVar10 = uVar7;
  puVar10[2] = uVar8;
  *(uint *)((int)puVar10 + uVar4) = uVar8;
  param_1[2] = iVar9 + 0x10;
  if (uVar8 < 0x4001) {
    uVar7 = uVar8 >> 4;
    iVar9 = uVar7 * 0x14 + 0x18;
  }
  else if ((int)uVar8 < 0) {
    iVar9 = 0x5180;
    uVar7 = 0x412;
  }
  else {
    uVar7 = uVar8;
    iVar9 = 0x1f;
    do {
      iVar5 = iVar9;
      uVar7 = uVar7 * 2;
      iVar9 = iVar5 + -1;
    } while (-1 < (int)uVar7);
    uVar7 = iVar5 + 0x3f2;
    iVar9 = uVar7 * 0x14 + 0x18;
  }
  puVar2 = (uint *)param_1[uVar7 * 5 + 7];
  uVar3 = *puVar2;
  if (puVar2 == (uint *)(iVar9 + (int)param_1)) goto LAB_100071ac;
  do {
    if (uVar8 <= uVar3) break;
    puVar2 = (uint *)puVar2[1];
    uVar3 = *puVar2;
  } while (puVar2 != (uint *)(iVar9 + (int)param_1));
LAB_100071ac:
  uVar8 = *(uint *)((int)puVar2 + uVar3 + 0xc);
  *(uint **)(uVar8 + 4) = puVar10 + 2;
  ((uint *)((int)puVar10 + uVar4))[1] = uVar8;
  puVar10[3] = (uint)puVar2;
  *(uint **)((int)puVar2 + uVar3 + 0xc) = puVar10 + 2;
  param_1[uVar7 * 5 + 10] = param_1[uVar7 * 5 + 10] + 1;
LAB_100071d4:
  uVar7 = param_1[2] + *puVar6;
  param_1[1] = param_1[1] + *puVar6;
  param_1[2] = uVar7;
  if ((uint)param_1[3] < uVar7) {
    param_1[3] = uVar7;
  }
  return puVar6 + 2;
LAB_1000720e:
  uVar8 = uVar8 + 1;
  puVar10 = puVar10 + 5;
  if (uVar8 == 0x413) {
    return (uint *)0x0;
  }
  goto LAB_100070d6;
}

