
int FUN_00489698(char *param_1,int param_2,int param_3,int param_4,int param_5,int *param_6,
                undefined4 param_7)

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
  int local_40;
  int local_3c;
  int local_38;
  int local_34;
  int local_30;
  char *local_28;
  
  if ((param_1 == (char *)0x0) || (*param_1 == '\0')) {
    iVar8 = 0;
  }
  else if (param_2 == 0) {
    iVar8 = 0;
  }
  else {
    local_38 = param_4;
    if (param_5 << 0x1f < 0) {
      local_38 = 0x1fffffff;
    }
    local_40 = 0;
    local_3c = 0;
    iVar6 = 0;
    iVar7 = 0;
    iVar8 = -1;
    local_30 = param_2;
    local_28 = param_1;
    iVar1 = (*(code *)*DAT_00489eac)(param_1,&local_40);
    local_3c = local_40;
    iVar5 = 0;
    local_40 = 0;
    local_34 = param_3;
    while (iVar9 = iVar1, iVar3 = local_40, iVar4 = iVar5, iVar5 = iVar4, local_40 = local_3c,
          local_28[iVar3] != '\0') {
      iVar6 = (*(code *)*DAT_00489eac)(local_28,&local_3c);
      iVar5 = iVar4 + 1;
      iVar1 = iVar6;
      if ((-1 < param_5 << 0x1c) || (iVar2 = FUN_00489652(param_7,iVar9), iVar2 == 0)) {
        iVar2 = FUN_004d57f4(local_30,iVar9,iVar6);
        iVar7 = iVar2 + iVar7;
        if (0 < iVar2) {
          iVar7 = local_34 + iVar7;
        }
        if (((iVar8 == -1) && (local_38 < iVar7 - local_34)) && (iVar8 = iVar3, param_5 << 0x1d < 0)
           ) break;
        if (((iVar9 == 10) || (iVar9 == 0xd)) || (iVar2 = FUN_004894a4(iVar9), iVar2 != 0)) {
          iVar5 = iVar4;
          if (((iVar3 == 0) && (iVar8 == -1)) && (param_6 != (int *)0x0)) {
            *param_6 = iVar7;
          }
          break;
        }
        iVar3 = FUN_004894d0(iVar6);
        if ((iVar3 != 0) || (iVar3 = FUN_004894d0(iVar9), iVar3 != 0)) {
          *param_6 = iVar7;
          iVar3 = local_40;
          break;
        }
        if ((param_6 != (int *)0x0) && (iVar8 == -1)) {
          *param_6 = iVar7;
        }
      }
    }
    if (iVar8 == -1) {
      if ((iVar5 == 0) || ((iVar8 = iVar3, iVar9 == 0xd && (iVar6 == 10)))) {
        iVar8 = local_40;
      }
    }
    else if (-1 < param_5 << 0x1d) {
      if (param_6 != (int *)0x0) {
        *param_6 = 0;
      }
      iVar8 = 0;
    }
  }
  return iVar8;
}

