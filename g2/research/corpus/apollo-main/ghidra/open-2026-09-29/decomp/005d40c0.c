
undefined4
FUN_005d40c0(int param_1,int *param_2,int *param_3,int *param_4,int *param_5,int *param_6)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  
  iVar6 = param_3[1];
  iVar1 = param_2[1];
  iVar7 = (*param_5 - *param_4) + 0x10 >> 5;
  iVar8 = (param_5[1] - param_4[1]) + 0x10 >> 5;
  iVar9 = *param_4;
  iVar2 = *param_2;
  iVar10 = param_4[1];
  iVar3 = param_2[1];
  iVar4 = FT_MulFix((*param_3 - *param_2) + 0x10 >> 5,iVar8);
  iVar1 = FT_MulFix((iVar6 - iVar1) + 0x10 >> 5,iVar7);
  if (iVar4 - iVar1 != 0) {
    iVar2 = FT_MulFix((iVar9 - iVar2) + 0x10 >> 5,iVar8);
    iVar3 = FT_MulFix((iVar10 - iVar3) + 0x10 >> 5,iVar7);
    uVar5 = FT_DivFix(iVar2 - iVar3,iVar4 - iVar1);
    iVar1 = FT_MulFix(uVar5,*param_3 - *param_2);
    *param_6 = iVar1 + *param_2;
    iVar1 = FT_MulFix(uVar5,param_3[1] - param_2[1]);
    param_6[1] = iVar1 + param_2[1];
    if (*param_2 == *param_3) {
      if (*param_6 - *param_2 < 0) {
        iVar1 = *param_2 - *param_6;
      }
      else {
        iVar1 = *param_6 - *param_2;
      }
      if (iVar1 < *(int *)(param_1 + 0x2db4)) {
        *param_6 = *param_2;
      }
    }
    if (param_2[1] == param_3[1]) {
      if (param_6[1] - param_2[1] < 0) {
        iVar1 = param_2[1] - param_6[1];
      }
      else {
        iVar1 = param_6[1] - param_2[1];
      }
      if (iVar1 < *(int *)(param_1 + 0x2db4)) {
        param_6[1] = param_2[1];
      }
    }
    if (*param_4 == *param_5) {
      if (*param_6 - *param_4 < 0) {
        iVar1 = *param_4 - *param_6;
      }
      else {
        iVar1 = *param_6 - *param_4;
      }
      if (iVar1 < *(int *)(param_1 + 0x2db4)) {
        *param_6 = *param_4;
      }
    }
    if (param_4[1] == param_5[1]) {
      if (param_6[1] - param_4[1] < 0) {
        iVar1 = param_4[1] - param_6[1];
      }
      else {
        iVar1 = param_6[1] - param_4[1];
      }
      if (iVar1 < *(int *)(param_1 + 0x2db4)) {
        param_6[1] = param_4[1];
      }
    }
    if (*param_6 - (*param_4 + *param_3) / 2 < 0) {
      iVar1 = (*param_4 + *param_3) / 2 - *param_6;
    }
    else {
      iVar1 = *param_6 - (*param_4 + *param_3) / 2;
    }
    if (iVar1 <= *(int *)(param_1 + 0x2db0)) {
      if (param_6[1] - (param_4[1] + param_3[1]) / 2 < 0) {
        iVar1 = (param_4[1] + param_3[1]) / 2 - param_6[1];
      }
      else {
        iVar1 = param_6[1] - (param_4[1] + param_3[1]) / 2;
      }
      if (iVar1 <= *(int *)(param_1 + 0x2db0)) {
        return 1;
      }
    }
  }
  return 0;
}

