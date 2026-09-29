
void FUN_005c3896(undefined4 *param_1,int *param_2)

{
  int *piVar1;
  
  piVar1 = (int *)param_2[2];
  param_2[2] = piVar1[1];
  if (piVar1[1] != 0) {
    *(int **)piVar1[1] = param_2;
  }
  *piVar1 = *param_2;
  if (*param_2 == 0) {
    *param_1 = piVar1;
  }
  else if (param_2 == *(int **)(*param_2 + 4)) {
    *(int **)(*param_2 + 4) = piVar1;
  }
  else {
    *(int **)(*param_2 + 8) = piVar1;
  }
  piVar1[1] = (int)param_2;
  *param_2 = (int)piVar1;
  return;
}

