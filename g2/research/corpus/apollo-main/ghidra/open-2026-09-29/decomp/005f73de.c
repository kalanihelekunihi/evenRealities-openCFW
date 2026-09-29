
void _iup_worker_interpolate(int *param_1,uint param_2,uint param_3,uint param_4,uint param_5)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  undefined4 uVar10;
  
  if (((param_2 <= param_3) && (param_4 < (uint)param_1[3])) && (param_5 < (uint)param_1[3])) {
    iVar7 = *(int *)(param_1[2] + param_4 * 8);
    iVar8 = *(int *)(param_1[2] + param_5 * 8);
    uVar5 = param_5;
    iVar6 = iVar7;
    if (iVar8 < iVar7) {
      uVar5 = param_4;
      param_4 = param_5;
      iVar6 = iVar8;
      iVar8 = iVar7;
    }
    iVar7 = *(int *)(*param_1 + param_4 * 8);
    iVar2 = *(int *)(*param_1 + uVar5 * 8);
    iVar9 = *(int *)(param_1[1] + param_4 * 8);
    iVar3 = *(int *)(param_1[1] + uVar5 * 8);
    if ((iVar9 == iVar3) || (iVar6 == iVar8)) {
      for (; param_2 <= param_3; param_2 = param_2 + 1) {
        iVar6 = *(int *)(*param_1 + param_2 * 8);
        if (iVar7 < iVar6) {
          iVar8 = iVar9;
          if (iVar2 <= iVar6) {
            iVar8 = (iVar3 - iVar2) + iVar6;
          }
        }
        else {
          iVar8 = (iVar9 - iVar7) + iVar6;
        }
        *(int *)(param_1[1] + param_2 * 8) = iVar8;
      }
    }
    else {
      uVar10 = 0;
      bVar1 = false;
      for (; param_2 <= param_3; param_2 = param_2 + 1) {
        iVar4 = *(int *)(*param_1 + param_2 * 8);
        if (iVar7 < iVar4) {
          if (iVar4 < iVar2) {
            if (!bVar1) {
              bVar1 = true;
              uVar10 = FT_DivFix(iVar3 - iVar9,iVar8 - iVar6);
            }
            iVar4 = FT_MulFix(*(int *)(param_1[2] + param_2 * 8) - iVar6,uVar10);
            iVar4 = iVar4 + iVar9;
          }
          else {
            iVar4 = (iVar3 - iVar2) + iVar4;
          }
        }
        else {
          iVar4 = (iVar9 - iVar7) + iVar4;
        }
        *(int *)(param_1[1] + param_2 * 8) = iVar4;
      }
    }
  }
  return;
}

