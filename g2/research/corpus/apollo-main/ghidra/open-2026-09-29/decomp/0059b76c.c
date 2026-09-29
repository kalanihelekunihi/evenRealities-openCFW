
void FUN_0059b76c(int param_1,int param_2,int param_3,float *param_4,int *param_5)

{
  int iVar1;
  int iVar2;
  int iVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  
  fVar4 = (float)FUN_0059b714(-param_3);
  iVar3 = 0;
  iVar2 = *(int *)(DAT_0059c178 + param_2 * 4) * (param_1 + 1);
  *param_5 = iVar2;
  if (0 < iVar2) {
    do {
      iVar1 = FUN_0059b6a0(param_2);
      if (iVar1 == 0) {
        fVar5 = 0.625;
      }
      else {
        fVar5 = 0.5;
      }
      fVar6 = *param_4;
      *param_4 = fVar6 * fVar4;
      fVar7 = param_4[1];
      param_4[1] = fVar7 * fVar4;
      iVar1 = iVar2;
      if (((int)((uint)(ABS(fVar6 * fVar4) < fVar5) << 0x1f) < 0) && (ABS(fVar7 * fVar4) < fVar5)) {
        iVar1 = *param_5 + -2;
      }
      iVar3 = iVar3 + 2;
      param_4 = param_4 + 2;
      *param_5 = iVar1;
    } while (iVar3 < iVar2);
  }
  return;
}

