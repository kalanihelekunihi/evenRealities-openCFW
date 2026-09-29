
void tt_interpolate_deltas(short *param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  short sVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  
  if (*param_1 != 0) {
    sVar1 = 0;
    iVar4 = 0;
    iVar8 = param_4;
    do {
      iVar2 = (int)*(short *)(*(int *)(param_1 + 6) + sVar1 * 2);
      for (iVar5 = iVar4; (iVar5 <= iVar2 && (*(char *)(param_4 + iVar5) == '\0'));
          iVar5 = iVar5 + 1) {
      }
      iVar3 = iVar5;
      iVar6 = iVar5;
      if (iVar5 <= iVar2) {
        while (iVar7 = iVar6, iVar6 = iVar7 + 1, iVar6 <= iVar2) {
          if (*(char *)(param_4 + iVar6) != '\0') {
            tt_delta_interpolate(iVar3 + 1,iVar7,iVar3,iVar6,param_3,param_2,param_2,param_4,iVar8);
            iVar3 = iVar6;
          }
        }
        if (iVar3 == iVar5) {
          tt_delta_shift(iVar4,iVar2,iVar3,param_3,param_2);
        }
        else {
          tt_delta_interpolate(iVar3 + 1,iVar2,iVar3,iVar5,param_3,param_2,param_2,param_4,iVar8);
          if (0 < iVar5) {
            tt_delta_interpolate(iVar4,iVar5 + -1,iVar3,iVar5,param_3,param_2);
          }
        }
      }
      sVar1 = sVar1 + 1;
      iVar4 = iVar6;
    } while (sVar1 < *param_1);
  }
  return;
}

