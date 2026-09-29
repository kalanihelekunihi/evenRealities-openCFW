
void FUN_0043ba6c(float *param_1,int *param_2,float *param_3,int *param_4)

{
  int iVar1;
  int iVar2;
  float fVar3;
  
  iVar2 = *param_2 * 2;
  *param_4 = *param_2;
  param_4[1] = 2;
  if (0 < iVar2) {
    iVar1 = 0;
    do {
      fVar3 = *param_1;
      param_1 = param_1 + 1;
      iVar1 = iVar1 + 1;
      *param_3 = ABS(fVar3);
      param_3 = param_3 + 1;
    } while (iVar2 - iVar1 != 0);
  }
  return;
}

