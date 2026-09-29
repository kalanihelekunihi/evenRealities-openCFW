
void FUN_00561964(undefined4 param_1,float *param_2)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  
  fVar1 = (float)FUN_00524130();
  fVar2 = (float)FUN_0052405c(param_1);
  fVar3 = *param_2;
  fVar4 = param_2[1];
  fVar5 = param_2[2];
  *param_2 = fVar1 * fVar3 - fVar2 * param_2[3];
  param_2[3] = fVar2 * fVar3 + fVar1 * param_2[3];
  param_2[1] = fVar1 * fVar4 - fVar2 * param_2[4];
  param_2[4] = fVar2 * fVar4 + fVar1 * param_2[4];
  param_2[2] = fVar1 * fVar5 - fVar2 * param_2[5];
  param_2[5] = fVar2 * fVar5 + fVar1 * param_2[5];
  return;
}

