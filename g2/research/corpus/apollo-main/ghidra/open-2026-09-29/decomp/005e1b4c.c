
void FUN_005e1b4c(int *param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  param_1[0xc] = param_1[6];
  iVar3 = param_1[2];
  iVar1 = (iVar3 + *param_1) / 2;
  param_1[2] = iVar1;
  iVar2 = (param_1[4] + param_1[6]) / 2;
  param_1[10] = iVar2;
  iVar3 = (param_1[4] + iVar3) / 2;
  iVar1 = (iVar3 + iVar1) / 2;
  param_1[4] = iVar1;
  iVar2 = (iVar3 + iVar2) / 2;
  param_1[8] = iVar2;
  param_1[6] = (iVar2 + iVar1) / 2;
  param_1[0xd] = param_1[7];
  iVar3 = param_1[3];
  iVar1 = (iVar3 + param_1[1]) / 2;
  param_1[3] = iVar1;
  iVar2 = (param_1[5] + param_1[7]) / 2;
  param_1[0xb] = iVar2;
  iVar3 = (param_1[5] + iVar3) / 2;
  iVar1 = (iVar3 + iVar1) / 2;
  param_1[5] = iVar1;
  iVar2 = (iVar3 + iVar2) / 2;
  param_1[9] = iVar2;
  param_1[7] = (iVar2 + iVar1) / 2;
  return;
}

