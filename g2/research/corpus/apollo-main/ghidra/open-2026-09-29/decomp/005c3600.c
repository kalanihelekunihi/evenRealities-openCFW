
int FUN_005c3600(int *param_1,int *param_2)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;
  undefined4 *puVar4;
  int iVar5;
  int iVar6;
  
  if ((param_2[1] == 0) || (param_2[2] == 0)) {
    if (param_2[2] == 0) {
      piVar1 = (int *)param_2[1];
    }
    else {
      piVar1 = (int *)param_2[2];
    }
    iVar5 = *param_2;
    iVar6 = param_2[3];
    if (piVar1 != (int *)0x0) {
      *piVar1 = iVar5;
    }
    if (iVar5 == 0) {
      *param_1 = (int)piVar1;
    }
    else if (*(int **)(iVar5 + 4) == param_2) {
      *(int **)(iVar5 + 4) = piVar1;
    }
    else {
      *(int **)(iVar5 + 8) = piVar1;
    }
    if ((char)iVar6 == '\x01') {
      FUN_005c3976(param_1);
    }
    iVar6 = param_2[4];
    FUN_0044f758(param_2);
  }
  else {
    piVar1 = (int *)thunk_FUN_005c379c(param_2[2]);
    if (*param_2 == 0) {
      *param_1 = (int)piVar1;
    }
    else if (*(int **)(*param_2 + 4) == param_2) {
      *(int **)(*param_2 + 4) = piVar1;
    }
    else {
      *(int **)(*param_2 + 8) = piVar1;
    }
    puVar4 = (undefined4 *)piVar1[2];
    piVar2 = (int *)*piVar1;
    iVar6 = piVar1[3];
    piVar3 = piVar1;
    if (piVar2 != param_2) {
      if (puVar4 != (undefined4 *)0x0) {
        *puVar4 = piVar2;
      }
      piVar2[1] = (int)puVar4;
      piVar1[2] = param_2[2];
      *(int **)param_2[2] = piVar1;
      piVar3 = piVar2;
    }
    *piVar1 = *param_2;
    *(char *)(piVar1 + 3) = (char)param_2[3];
    piVar1[1] = param_2[1];
    *(int **)param_2[1] = piVar1;
    if ((char)iVar6 == '\x01') {
      FUN_005c3976(param_1,puVar4,piVar3);
    }
    iVar6 = param_2[4];
    FUN_0044f758(param_2);
  }
  return iVar6;
}

