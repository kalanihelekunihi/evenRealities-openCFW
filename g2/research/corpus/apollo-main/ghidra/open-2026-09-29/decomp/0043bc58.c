
void FUN_0043bc58(float *param_1,int param_2,float *param_3,undefined4 *param_4)

{
  int iVar1;
  int iVar2;
  float fVar3;
  
  iVar2 = *(int *)(param_2 + 4);
  *param_4 = 1;
  param_4[1] = *(undefined4 *)(param_2 + 4);
  if (0 < iVar2) {
    iVar1 = 0;
    do {
      fVar3 = *param_1;
      param_1 = param_1 + 1;
      iVar1 = iVar1 + 1;
      *param_3 = ABS(fVar3);
      param_3 = param_3 + 1;
    } while (iVar2 != iVar1);
  }
  return;
}

