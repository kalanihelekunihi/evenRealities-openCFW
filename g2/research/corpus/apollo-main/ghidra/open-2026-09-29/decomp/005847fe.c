
int FUN_005847fe(char *param_1,undefined4 param_2,undefined4 param_3)

{
  int *piVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  bool bVar5;
  undefined4 uVar6;
  
  piVar1 = DAT_00584994;
  bVar5 = true;
  if (*DAT_00584994 == 0) {
    *DAT_00584994 = DAT_00584998;
    while (*piVar1 != 0) {
      uVar6 = **(undefined4 **)*piVar1;
      iVar3 = FUN_0044a43c(uVar6);
      iVar4 = FUN_0044b610(param_1,uVar6,iVar3);
      if ((iVar4 == 0) && ((param_1[iVar3] == ' ' || (param_1[iVar3] == '\0')))) {
        if (-1 < *(char *)(*(int *)*piVar1 + 0xc)) {
          cVar2 = FUN_005849a8(param_1);
          if (cVar2 != *(char *)(*(int *)*piVar1 + 0xc)) {
            bVar5 = false;
          }
        }
        break;
      }
      *piVar1 = *(int *)(*piVar1 + 4);
    }
  }
  if ((*piVar1 == 0) || (bVar5)) {
    if (*piVar1 == 0) {
      iVar3 = FUN_0044a43c(param_1);
      if (((iVar3 != 1) || (*param_1 != '\r')) &&
         ((iVar3 = FUN_0044a43c(param_1), iVar3 != 0 || (*param_1 != '\0')))) {
        FUN_0044b5a0(param_2,DAT_005849a0,param_3);
      }
      iVar3 = 0;
    }
    else {
      iVar3 = (**(code **)(*(int *)*piVar1 + 8))(param_2,param_3,param_1);
      if (iVar3 == 0) {
        *piVar1 = 0;
      }
    }
  }
  else {
    FUN_0044b5a0(param_2,DAT_0058499c,param_3);
    *piVar1 = 0;
    iVar3 = 0;
  }
  return iVar3;
}

