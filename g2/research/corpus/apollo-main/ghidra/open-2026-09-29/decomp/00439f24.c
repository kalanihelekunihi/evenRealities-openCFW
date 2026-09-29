
float FUN_00439f24(float *param_1)

{
  int iVar1;
  float fVar2;
  float fVar3;
  
  iVar1 = FUN_0043a0f4(*param_1);
  if (iVar1 == 0) {
    fVar2 = *param_1;
    iVar1 = 2;
  }
  else {
    iVar1 = FUN_0043a0f4(param_1[1]);
    if (iVar1 != 0) {
      iVar1 = FUN_0043a0f4(param_1[2]);
      if (iVar1 == 0) {
        return param_1[2];
      }
      return *param_1;
    }
    fVar2 = param_1[1];
    iVar1 = 3;
  }
  param_1 = param_1 + iVar1 + 0x3fffffff;
  while( true ) {
    fVar3 = *param_1;
    param_1 = param_1 + 1;
    if ((int)((uint)(fVar3 < fVar2) << 0x1f) < 0) {
      fVar2 = fVar3;
    }
    if (iVar1 != 2) break;
    iVar1 = 3;
  }
  return fVar2;
}

