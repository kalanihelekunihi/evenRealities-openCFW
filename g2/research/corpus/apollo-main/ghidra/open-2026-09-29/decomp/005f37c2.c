
void tt_delta_interpolate(int param_1,int param_2,int param_3,int param_4,int param_5,int param_6)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  
  if (param_1 <= param_2) {
    for (iVar6 = 0; iVar6 < 2; iVar6 = iVar6 + 1) {
      param_5 = param_5 + iVar6 * 4;
      param_6 = param_6 + iVar6 * 4;
      iVar7 = param_3;
      if (*(int *)(param_5 + param_4 * 8) < *(int *)(param_5 + param_3 * 8)) {
        iVar7 = param_4;
        param_4 = param_3;
      }
      iVar8 = *(int *)(param_5 + iVar7 * 8);
      iVar1 = *(int *)(param_5 + param_4 * 8);
      iVar2 = *(int *)(param_6 + iVar7 * 8);
      iVar3 = *(int *)(param_6 + param_4 * 8);
      if ((iVar8 != iVar1) || (iVar2 == iVar3)) {
        iVar9 = param_1;
        if (iVar8 == iVar1) {
          uVar4 = 0;
        }
        else {
          uVar4 = FT_DivFix(iVar3 - iVar2,iVar1 - iVar8);
        }
        for (; iVar9 <= param_2; iVar9 = iVar9 + 1) {
          iVar5 = *(int *)(param_5 + iVar9 * 8);
          if (iVar8 < iVar5) {
            if (iVar5 < iVar1) {
              iVar5 = FT_MulFix(iVar5 - iVar8,uVar4);
              iVar5 = iVar5 + iVar2;
            }
            else {
              iVar5 = (iVar3 - iVar1) + iVar5;
            }
          }
          else {
            iVar5 = (iVar2 - iVar8) + iVar5;
          }
          *(int *)(param_6 + iVar9 * 8) = iVar5;
        }
      }
      param_3 = iVar7;
    }
  }
  return;
}

