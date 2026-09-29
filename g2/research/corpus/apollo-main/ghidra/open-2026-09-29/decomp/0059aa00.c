
void FUN_0059aa00(int *param_1,uint param_2,float *param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  float fVar4;
  
  iVar1 = DAT_0059b5bc;
  if ((int)param_2 < 1) {
    return;
  }
  if ((int)(param_2 << 0x1f) < 0) {
    iVar2 = *param_1;
    iVar3 = iVar2;
    if (iVar2 < 0) {
      iVar3 = -iVar2;
    }
    fVar4 = *(float *)(DAT_0059b5bc + iVar3 * 4);
    if (iVar2 < 0) {
      fVar4 = -fVar4;
    }
    *param_3 = fVar4;
    param_3 = param_3 + 1;
    param_1 = param_1 + 1;
  }
  if (param_2 >> 1 == 0) {
    return;
  }
  do {
    iVar2 = *param_1;
    iVar3 = iVar2;
    if (iVar2 < 0) {
      iVar3 = -iVar2;
    }
    fVar4 = *(float *)(iVar1 + iVar3 * 4);
    if (iVar2 < 0) {
      fVar4 = -fVar4;
    }
    *param_3 = fVar4;
    iVar2 = param_1[1];
    iVar3 = iVar2;
    if (iVar2 < 0) {
      iVar3 = -iVar2;
    }
    fVar4 = *(float *)(iVar1 + iVar3 * 4);
    if (iVar2 < 0) {
      fVar4 = -fVar4;
    }
    param_3[1] = fVar4;
    param_3 = param_3 + 2;
    param_1 = param_1 + 2;
    loopEnd();
  } while( true );
}

