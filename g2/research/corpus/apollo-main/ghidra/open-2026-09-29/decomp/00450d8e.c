
void FUN_00450d8e(int *param_1,int *param_2,int *param_3)

{
  int iVar1;
  
  if (*param_2 < *param_3) {
    iVar1 = *param_2;
  }
  else {
    iVar1 = *param_3;
  }
  *param_1 = iVar1;
  if (param_2[1] < param_3[1]) {
    iVar1 = param_2[1];
  }
  else {
    iVar1 = param_3[1];
  }
  param_1[1] = iVar1;
  if (param_3[2] < param_2[2]) {
    iVar1 = param_2[2];
  }
  else {
    iVar1 = param_3[2];
  }
  param_1[2] = iVar1;
  if (param_3[3] < param_2[3]) {
    iVar1 = param_2[3];
  }
  else {
    iVar1 = param_3[3];
  }
  param_1[3] = iVar1;
  return;
}

