
undefined1 FUN_00450bcc(int *param_1,int *param_2,int *param_3)

{
  undefined1 uVar1;
  int iVar2;
  
  if (*param_3 < *param_2) {
    iVar2 = *param_2;
  }
  else {
    iVar2 = *param_3;
  }
  *param_1 = iVar2;
  if (param_3[1] < param_2[1]) {
    iVar2 = param_2[1];
  }
  else {
    iVar2 = param_3[1];
  }
  param_1[1] = iVar2;
  if (param_2[2] < param_3[2]) {
    iVar2 = param_2[2];
  }
  else {
    iVar2 = param_3[2];
  }
  param_1[2] = iVar2;
  if (param_2[3] < param_3[3]) {
    iVar2 = param_2[3];
  }
  else {
    iVar2 = param_3[3];
  }
  param_1[3] = iVar2;
  uVar1 = 1;
  if ((param_1[2] < *param_1) || (param_1[3] < param_1[1])) {
    uVar1 = 0;
  }
  return uVar1;
}

