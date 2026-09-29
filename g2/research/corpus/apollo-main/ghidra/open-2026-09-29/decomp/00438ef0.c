
float FUN_00438ef0(float *param_1,int param_2)

{
  int iVar1;
  float *pfVar2;
  float fVar3;
  
  iVar1 = param_2 + 4;
  pfVar2 = (float *)(DAT_004396b4 +
                    (iVar1 - (iVar1 + ((uint)(iVar1 >> 1) >> 0x1e) & 0xfffffffc)) * 0x20);
  if (param_2 < 0) {
    fVar3 = *pfVar2;
    pfVar2 = pfVar2 + 1;
    fVar3 = param_1[-4] * fVar3;
  }
  else {
    fVar3 = DAT_00438f9c;
    if (0 < param_2) {
      fVar3 = param_1[4] * pfVar2[7];
    }
  }
  return param_1[-3] * *pfVar2 + param_1[-2] * pfVar2[1] + param_1[-1] * pfVar2[2] +
         *param_1 * pfVar2[3] + param_1[1] * pfVar2[4] + param_1[2] * pfVar2[5] +
         param_1[3] * pfVar2[6] + fVar3;
}

