
void FUN_005d2a18(int param_1,undefined4 param_2,int param_3,int *param_4,int param_5,char param_6,
                 int *param_7)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  
  *param_4 = 0;
  if ((param_5 == 0) && (param_6 == '\0')) {
    return;
  }
  if (param_1 < 0x28f) {
    return;
  }
  if (param_6 == '\0') goto LAB_005d2b82;
  iVar8 = *param_7;
  iVar9 = param_7[1];
  iVar10 = param_7[2];
  iVar5 = param_7[3];
  iVar11 = param_7[4];
  iVar6 = param_7[5];
  iVar7 = param_7[6];
  iVar1 = param_7[7];
  iVar2 = FT_MulFix(param_5 + param_3,param_1);
  iVar3 = FT_MSB(iVar2);
  iVar4 = FT_MSB(param_2);
  if (iVar4 + iVar3 < 0x2e) {
    iVar3 = FT_MulFix(iVar2,param_2);
  }
  else {
    iVar3 = iVar7 << 0x10;
  }
  if (iVar3 < iVar8 * 0x10000) {
    iVar1 = FT_DivFix(iVar9 << 0x10,param_2);
    *param_4 = iVar1;
  }
  else if (iVar3 < iVar10 * 0x10000) {
    iVar3 = FT_DivFix(iVar8 << 0x10,param_2);
    if (iVar10 - iVar8 == 0) {
LAB_005d2b00:
      iVar3 = FT_DivFix(iVar10 << 0x10,param_2);
      if (iVar11 - iVar10 == 0) {
LAB_005d2b44:
        iVar3 = FT_DivFix(iVar11 << 0x10,param_2);
        if (iVar7 - iVar11 == 0) goto LAB_005d2b6a;
        iVar1 = FT_MulDiv(iVar2 - iVar3,iVar1 - iVar6,iVar7 - iVar11);
        iVar2 = FT_DivFix(iVar6 << 0x10,param_2);
        *param_4 = iVar2 + iVar1;
      }
      else {
        iVar1 = FT_MulDiv(iVar2 - iVar3,iVar6 - iVar5,iVar11 - iVar10);
        iVar2 = FT_DivFix(iVar5 << 0x10,param_2);
        *param_4 = iVar2 + iVar1;
      }
    }
    else {
      iVar1 = FT_MulDiv(iVar2 - iVar3,iVar5 - iVar9,iVar10 - iVar8);
      iVar2 = FT_DivFix(iVar9 << 0x10,param_2);
      *param_4 = iVar2 + iVar1;
    }
  }
  else {
    if (iVar3 < iVar11 * 0x10000) goto LAB_005d2b00;
    if (iVar3 < iVar7 * 0x10000) goto LAB_005d2b44;
LAB_005d2b6a:
    iVar1 = FT_DivFix(iVar1 << 0x10,param_2);
    *param_4 = iVar1;
  }
  iVar1 = FT_DivFix(*param_4,param_1 << 1);
  *param_4 = iVar1;
LAB_005d2b82:
  *param_4 = param_5 / 2 + *param_4;
  return;
}

