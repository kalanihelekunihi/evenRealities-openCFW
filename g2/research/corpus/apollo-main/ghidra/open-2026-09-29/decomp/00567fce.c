
void FUN_00567fce(int *param_1)

{
  int iVar1;
  int iVar2;
  
  param_1[8] = param_1[4];
  iVar1 = (param_1[2] + param_1[4]) / 2;
  param_1[6] = iVar1;
  iVar2 = (param_1[2] + *param_1) / 2;
  param_1[2] = iVar2;
  param_1[4] = (iVar2 + iVar1) / 2;
  param_1[9] = param_1[5];
  iVar1 = (param_1[3] + param_1[5]) / 2;
  param_1[7] = iVar1;
  iVar2 = (param_1[3] + param_1[1]) / 2;
  param_1[3] = iVar2;
  param_1[5] = (iVar2 + iVar1) / 2;
  return;
}

