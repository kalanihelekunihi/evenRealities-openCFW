
int ft_var_to_design(int param_1,uint param_2,int param_3,int param_4)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint *puVar5;
  ushort *puVar6;
  uint uVar7;
  
  puVar5 = *(uint **)(param_1 + 700);
  uVar4 = param_2;
  if (*puVar5 < param_2) {
    uVar4 = *puVar5;
  }
  for (uVar1 = 0; uVar1 < uVar4; uVar1 = uVar1 + 1) {
    *(undefined4 *)(param_4 + uVar1 * 4) = *(undefined4 *)(param_3 + uVar1 * 4);
  }
  for (; uVar1 < param_2; uVar1 = uVar1 + 1) {
    *(undefined4 *)(param_4 + uVar1 * 4) = 0;
  }
  if (puVar5[7] != 0) {
    puVar6 = (ushort *)puVar5[7];
    for (uVar1 = 0; uVar1 < uVar4; uVar1 = uVar1 + 1) {
      for (uVar7 = 1; uVar7 < *puVar6; uVar7 = uVar7 + 1) {
        if (*(int *)(param_4 + uVar1 * 4) < *(int *)(*(int *)(puVar6 + 2) + uVar7 * 8 + 4)) {
          iVar2 = FT_MulDiv(*(int *)(param_4 + uVar1 * 4) -
                            *(int *)(*(int *)(puVar6 + 2) + uVar7 * 8 + -4),
                            *(int *)(*(int *)(puVar6 + 2) + uVar7 * 8) -
                            *(int *)(*(int *)(puVar6 + 2) + uVar7 * 8 + -8),
                            *(int *)(*(int *)(puVar6 + 2) + uVar7 * 8 + 4) -
                            *(int *)(*(int *)(puVar6 + 2) + uVar7 * 8 + -4));
          *(int *)(param_4 + uVar1 * 4) = *(int *)(*(int *)(puVar6 + 2) + uVar7 * 8 + -8) + iVar2;
          break;
        }
      }
      puVar6 = puVar6 + 4;
    }
  }
  iVar2 = *(int *)(puVar5[3] + 0xc);
  for (uVar1 = 0; uVar1 < uVar4; uVar1 = uVar1 + 1) {
    if (*(int *)(param_4 + uVar1 * 4) < 0) {
      iVar3 = FT_MulFix(*(undefined4 *)(param_4 + uVar1 * 4),
                        *(int *)(iVar2 + 8) - *(int *)(iVar2 + 4));
      *(int *)(param_4 + uVar1 * 4) = iVar3 + *(int *)(iVar2 + 8);
    }
    else if (*(int *)(param_4 + uVar1 * 4) < 1) {
      *(undefined4 *)(param_4 + uVar1 * 4) = *(undefined4 *)(iVar2 + 8);
    }
    else {
      iVar3 = FT_MulFix(*(undefined4 *)(param_4 + uVar1 * 4),
                        *(int *)(iVar2 + 0xc) - *(int *)(iVar2 + 8));
      *(int *)(param_4 + uVar1 * 4) = iVar3 + *(int *)(iVar2 + 8);
    }
    iVar2 = iVar2 + 0x18;
  }
  return param_4;
}

