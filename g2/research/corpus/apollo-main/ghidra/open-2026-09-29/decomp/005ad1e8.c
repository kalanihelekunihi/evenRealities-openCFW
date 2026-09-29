
undefined4 cff_parse_font_matrix(int param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int aiStack_54 [6];
  int aiStack_3c [6];
  
  iVar1 = *(int *)(param_1 + 0x20);
  iVar7 = *(int *)(param_1 + 0x10);
  uVar3 = 0xa1;
  if (*(int *)(param_1 + 0x10) + 0x18U <= *(uint *)(param_1 + 0x14)) {
    uVar3 = 0;
    *(undefined1 *)(iVar1 + 0x40) = 1;
    iVar4 = -0x80000000;
    iVar5 = 0x7fffffff;
    for (iVar6 = 0; iVar6 < 6; iVar6 = iVar6 + 1) {
      iVar2 = cff_parse_fixed_dynamic(param_1,iVar7,aiStack_54 + iVar6);
      iVar7 = iVar7 + 4;
      aiStack_3c[iVar6] = iVar2;
      if (aiStack_3c[iVar6] != 0) {
        if (iVar4 < aiStack_54[iVar6]) {
          iVar4 = aiStack_54[iVar6];
        }
        if (aiStack_54[iVar6] < iVar5) {
          iVar5 = aiStack_54[iVar6];
        }
      }
    }
    if ((iVar4 + 9U < 10) && ((uint)(iVar4 - iVar5) < 10)) {
      for (iVar7 = 0; iVar7 < 6; iVar7 = iVar7 + 1) {
        iVar5 = aiStack_3c[iVar7];
        if (iVar5 != 0) {
          iVar6 = *(int *)(DAT_005ad768 + (iVar4 - aiStack_54[iVar7]) * 4);
          iVar2 = iVar6 >> 1;
          if (iVar5 < 0) {
            if (iVar2 + -0x80000000 < iVar5) {
              aiStack_3c[iVar7] = (iVar5 - iVar2) / iVar6;
            }
            else {
              aiStack_3c[iVar7] = -0x80000000 / iVar6;
            }
          }
          else if (iVar5 < 0x7fffffff - iVar2) {
            aiStack_3c[iVar7] = (iVar2 + iVar5) / iVar6;
          }
          else {
            aiStack_3c[iVar7] = 0x7fffffff / iVar6;
          }
        }
      }
      *(int *)(iVar1 + 0x30) = aiStack_3c[0];
      *(int *)(iVar1 + 0x38) = aiStack_3c[1];
      *(int *)(iVar1 + 0x34) = aiStack_3c[2];
      *(int *)(iVar1 + 0x3c) = aiStack_3c[3];
      *(undefined4 *)(iVar1 + 0x48) = aiStack_3c[4];
      *(int *)(iVar1 + 0x4c) = aiStack_3c[5];
      *(undefined4 *)(iVar1 + 0x44) = *(undefined4 *)(DAT_005ad768 + iVar4 * -4);
    }
    else {
      *(int *)(iVar1 + 0x30) = 0x10000;
      *(undefined4 *)(iVar1 + 0x38) = 0;
      *(undefined4 *)(iVar1 + 0x34) = 0;
      *(undefined4 *)(iVar1 + 0x3c) = 0x10000;
      *(undefined4 *)(iVar1 + 0x48) = 0;
      *(undefined4 *)(iVar1 + 0x4c) = 0;
      *(undefined4 *)(iVar1 + 0x44) = 1;
    }
  }
  return uVar3;
}

