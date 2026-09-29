
void FUN_00599328(undefined4 param_1,undefined4 param_2,float *param_3,int param_4)

{
  float *pfVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float afStack_10c [62];
  
  fVar2 = *param_3;
  if (param_4 != 0) {
    fVar2 = -fVar2;
  }
  pfVar1 = afStack_10c;
  do {
    param_3 = param_3 + 1;
    fVar3 = *param_3;
    if (param_4 != 0) {
      fVar3 = -fVar3;
    }
    fVar4 = fVar3 - fVar2;
    *pfVar1 = fVar4 * 0.125 + fVar2;
    pfVar1[1] = fVar4 * 0.375 + fVar2;
    pfVar1[2] = fVar2 + fVar4 * 0.625;
    pfVar1[3] = fVar2 + fVar4 * 0.875;
    pfVar1 = pfVar1 + 4;
    loopEnd();
    fVar2 = fVar3;
  } while( true );
}

