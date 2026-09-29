
void FUN_10007240(int param_1,int param_2)

{
  int iVar1;
  uint *puVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint *puVar6;
  uint uVar7;
  uint *puVar8;
  int *piVar9;
  
  if (param_2 != 0) {
    puVar8 = (uint *)(param_2 + -8);
    uVar7 = *puVar8;
    *(uint *)(param_1 + 4) = *(int *)(param_1 + 4) - uVar7;
    *(uint *)(param_1 + 8) = *(int *)(param_1 + 8) - uVar7;
    puVar2 = (uint *)((int)puVar8 + uVar7 + 0x10);
    if ((puVar2 < *(uint **)(param_1 + 0x14)) && (piVar9 = (int *)puVar2[1], piVar9 != (int *)0x0))
    {
      uVar5 = *puVar2;
      iVar3 = *(int *)((int)puVar2 + uVar5 + 0xc);
      *(int **)(iVar3 + 4) = piVar9;
      uVar7 = uVar7 + 0x10 + uVar5;
      *(int *)((int)piVar9 + *piVar9 + 0xc) = iVar3;
      *(int *)(param_1 + 8) = *(int *)(param_1 + 8) + -0x10;
      if (uVar5 < 0x4001) {
        uVar5 = uVar5 >> 4;
      }
      else if ((int)uVar5 < 0) {
        uVar5 = 0x412;
      }
      else {
        iVar3 = 0x1f;
        do {
          iVar1 = iVar3;
          uVar5 = uVar5 * 2;
          iVar3 = iVar1 + -1;
        } while (-1 < (int)uVar5);
        uVar5 = iVar1 + 0x3f2;
      }
      iVar3 = param_1 + uVar5 * 0x14;
      *(int *)(iVar3 + 0x28) = *(int *)(iVar3 + 0x28) + -1;
    }
    if (*(uint **)(param_1 + 0x10) < puVar8) {
      puVar2 = (uint *)((int)puVar8 + (-0x10 - *(int *)(param_2 + -0x10)));
      piVar9 = *(int **)((int)puVar8 + (-0xc - *(int *)(param_2 + -0x10)));
      if (piVar9 != (int *)0x0) {
        uVar5 = *puVar2;
        iVar3 = *(int *)((int)puVar2 + uVar5 + 0xc);
        *(int **)(iVar3 + 4) = piVar9;
        *(int *)((int)piVar9 + *piVar9 + 0xc) = iVar3;
        uVar7 = uVar7 + uVar5 + 0x10;
        *(int *)(param_1 + 8) = *(int *)(param_1 + 8) + -0x10;
        if (uVar5 < 0x4001) {
          uVar5 = uVar5 >> 4;
        }
        else if ((int)uVar5 < 0) {
          uVar5 = 0x412;
        }
        else {
          iVar3 = 0x1f;
          do {
            iVar1 = iVar3;
            uVar5 = uVar5 * 2;
            iVar3 = iVar1 + -1;
          } while (-1 < (int)uVar5);
          uVar5 = iVar1 + 0x3f2;
        }
        iVar3 = param_1 + uVar5 * 0x14;
        *(int *)(iVar3 + 0x28) = *(int *)(iVar3 + 0x28) + -1;
        puVar8 = puVar2;
      }
    }
    puVar2 = (uint *)((int)puVar8 + uVar7 + 8);
    *puVar8 = uVar7;
    *puVar2 = uVar7;
    if (uVar7 < 0x4001) {
      uVar5 = uVar7 >> 4;
      iVar3 = uVar5 * 0x14 + 0x18;
    }
    else if ((int)uVar7 < 0) {
      iVar3 = 0x5180;
      uVar5 = 0x412;
    }
    else {
      iVar3 = 0x1f;
      uVar5 = uVar7;
      do {
        iVar1 = iVar3;
        uVar5 = uVar5 * 2;
        iVar3 = iVar1 + -1;
      } while (-1 < (int)uVar5);
      uVar5 = iVar1 + 0x3f2;
      iVar3 = uVar5 * 0x14 + 0x18;
    }
    puVar6 = *(uint **)(param_1 + uVar5 * 0x14 + 0x1c);
    uVar4 = *puVar6;
    while ((puVar6 != (uint *)(iVar3 + param_1) && (uVar4 < uVar7))) {
      puVar6 = (uint *)puVar6[1];
      uVar4 = *puVar6;
    }
    uVar7 = *(uint *)((int)puVar6 + uVar4 + 0xc);
    *(uint **)(uVar7 + 4) = puVar8;
    puVar2[1] = uVar7;
    puVar8[1] = (uint)puVar6;
    param_1 = param_1 + uVar5 * 0x14;
    *(uint **)((int)puVar6 + uVar4 + 0xc) = puVar8;
    *(int *)(param_1 + 0x28) = *(int *)(param_1 + 0x28) + 1;
  }
  return;
}

