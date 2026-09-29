
void ft_var_to_normalized(int param_1,uint param_2,int param_3,int param_4)

{
  undefined4 uVar1;
  int iVar2;
  ushort *puVar3;
  int iVar4;
  uint *puVar5;
  uint uVar6;
  uint uVar7;
  
  iVar4 = *(int *)(param_1 + 700);
  puVar5 = *(uint **)(iVar4 + 0xc);
  if (*puVar5 < param_2) {
    param_2 = *puVar5;
  }
  uVar6 = puVar5[3];
  for (uVar7 = 0; uVar7 < param_2; uVar7 = uVar7 + 1) {
    iVar2 = *(int *)(param_3 + uVar7 * 4);
    if ((*(int *)(uVar6 + 0xc) < iVar2) || (iVar2 < *(int *)(uVar6 + 4))) {
      if (*(int *)(uVar6 + 0xc) < iVar2) {
        iVar2 = *(int *)(uVar6 + 0xc);
      }
      else {
        iVar2 = *(int *)(uVar6 + 4);
      }
    }
    if (iVar2 < *(int *)(uVar6 + 8)) {
      iVar2 = FT_DivFix(iVar2 - *(int *)(uVar6 + 8),*(int *)(uVar6 + 4) - *(int *)(uVar6 + 8));
      *(int *)(param_4 + uVar7 * 4) = -iVar2;
    }
    else if (*(int *)(uVar6 + 8) < iVar2) {
      uVar1 = FT_DivFix(iVar2 - *(int *)(uVar6 + 8),*(int *)(uVar6 + 0xc) - *(int *)(uVar6 + 8));
      *(undefined4 *)(param_4 + uVar7 * 4) = uVar1;
    }
    else {
      *(undefined4 *)(param_4 + uVar7 * 4) = 0;
    }
    uVar6 = uVar6 + 0x18;
  }
  for (; uVar7 < *puVar5; uVar7 = uVar7 + 1) {
    *(undefined4 *)(param_4 + uVar7 * 4) = 0;
  }
  if (*(int *)(iVar4 + 0x1c) != 0) {
    puVar3 = *(ushort **)(iVar4 + 0x1c);
    for (uVar6 = 0; uVar6 < *puVar5; uVar6 = uVar6 + 1) {
      for (uVar7 = 1; uVar7 < *puVar3; uVar7 = uVar7 + 1) {
        if (*(int *)(param_4 + uVar6 * 4) < *(int *)(*(int *)(puVar3 + 2) + uVar7 * 8)) {
          iVar4 = FT_MulDiv(*(int *)(param_4 + uVar6 * 4) -
                            *(int *)(*(int *)(puVar3 + 2) + uVar7 * 8 + -8),
                            *(int *)(*(int *)(puVar3 + 2) + uVar7 * 8 + 4) -
                            *(int *)(*(int *)(puVar3 + 2) + uVar7 * 8 + -4),
                            *(int *)(*(int *)(puVar3 + 2) + uVar7 * 8) -
                            *(int *)(*(int *)(puVar3 + 2) + uVar7 * 8 + -8));
          *(int *)(param_4 + uVar6 * 4) = *(int *)(*(int *)(puVar3 + 2) + uVar7 * 8 + -4) + iVar4;
          break;
        }
      }
      puVar3 = puVar3 + 4;
    }
  }
  return;
}

