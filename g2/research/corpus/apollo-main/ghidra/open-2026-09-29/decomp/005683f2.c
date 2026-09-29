
undefined8 FUN_005683f2(int *param_1,int *param_2,undefined1 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  int iVar4;
  int iVar5;
  
  iVar1 = 0;
  if ((char)param_1[4] == '\0') {
    if (((*param_1 != 0) && ((*(int *)(param_1[2] + *param_1 * 8 + -8) - *param_2) + 1U < 3)) &&
       ((*(int *)(param_1[2] + *param_1 * 8 + -4) - param_2[1]) + 1U < 3)) goto LAB_00568478;
    iVar1 = FUN_005682de(param_1,1);
    if (iVar1 == 0) {
      piVar3 = (int *)(param_1[2] + *param_1 * 8);
      iVar2 = param_1[3];
      iVar4 = *param_1;
      iVar5 = param_2[1];
      *piVar3 = *param_2;
      piVar3[1] = iVar5;
      *(undefined1 *)(iVar2 + iVar4) = 1;
      *param_1 = *param_1 + 1;
    }
  }
  else {
    iVar2 = param_1[2] + *param_1 * 8;
    iVar4 = param_2[1];
    *(int *)(iVar2 + -8) = *param_2;
    *(int *)(iVar2 + -4) = iVar4;
  }
  *(undefined1 *)(param_1 + 4) = param_3;
LAB_00568478:
  return CONCAT44(param_4,iVar1);
}

