
undefined8 ft_var_get_item_delta(int param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  undefined4 uVar8;
  int *piVar9;
  uint uVar10;
  
  iVar6 = 0;
  iVar1 = *(int *)(param_2 + 4) + param_3 * 0x10;
  iVar2 = *(int *)(iVar1 + 0xc);
  iVar5 = *(int *)(iVar1 + 4);
  for (uVar7 = 0; uVar7 < *(uint *)(iVar1 + 4); uVar7 = uVar7 + 1) {
    uVar8 = 0x10000;
    piVar9 = *(int **)(*(int *)(param_2 + 0x10) + *(int *)(*(int *)(iVar1 + 8) + uVar7 * 4) * 4);
    for (uVar10 = 0; uVar10 < *(ushort *)(param_2 + 8); uVar10 = uVar10 + 1) {
      uVar4 = 0x10000;
      if ((*piVar9 <= piVar9[1]) && (piVar9[1] <= piVar9[2])) {
        if ((*piVar9 < 0) && ((0 < piVar9[2] && (piVar9[1] != 0)))) {
          uVar4 = 0x10000;
        }
        else if (piVar9[1] == 0) {
          uVar4 = 0x10000;
        }
        else if ((*(int *)(*(int *)(*(int *)(param_1 + 700) + 8) + uVar10 * 4) < *piVar9) ||
                (piVar9[2] < *(int *)(*(int *)(*(int *)(param_1 + 700) + 8) + uVar10 * 4))) {
          uVar4 = 0;
        }
        else if (*(int *)(*(int *)(*(int *)(param_1 + 700) + 8) + uVar10 * 4) == piVar9[1]) {
          uVar4 = 0x10000;
        }
        else if (*(int *)(*(int *)(*(int *)(param_1 + 700) + 8) + uVar10 * 4) < piVar9[1]) {
          uVar4 = FT_DivFix(*(int *)(*(int *)(*(int *)(param_1 + 700) + 8) + uVar10 * 4) - *piVar9,
                            piVar9[1] - *piVar9);
        }
        else {
          uVar4 = FT_DivFix(piVar9[2] - *(int *)(*(int *)(*(int *)(param_1 + 700) + 8) + uVar10 * 4)
                            ,piVar9[2] - piVar9[1]);
        }
      }
      uVar8 = FT_MulFix(uVar8,uVar4);
      piVar9 = piVar9 + 3;
    }
    iVar3 = FT_MulFix(uVar8,(int)*(short *)(iVar2 + param_4 * iVar5 * 2 + uVar7 * 2) << 0x10);
    iVar6 = iVar3 + iVar6;
  }
  return CONCAT44(iVar1,(int)(short)((uint)(iVar6 + 0x8000) >> 0x10));
}

