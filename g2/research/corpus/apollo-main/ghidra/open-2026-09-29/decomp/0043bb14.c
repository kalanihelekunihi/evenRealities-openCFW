
/* WARNING: Type propagation algorithm not settling */

float FUN_0043bb14(float param_1,float *param_2,int param_3,float *param_4,undefined4 *param_5)

{
  int iVar1;
  float *pfVar2;
  float *pfVar3;
  float *pfVar4;
  bool bVar5;
  uint in_fpscr;
  float fVar6;
  float fVar7;
  float local_4c [4];
  float local_3c [4];
  
  if (param_3 == 1) {
    *param_5 = 1;
    param_5[1] = 1;
    *param_4 = param_1 / *param_2;
    return param_1;
  }
  if (param_3 < 1) {
    *param_5 = 1;
    param_5[1] = param_3;
    return ABS(local_3c[0]);
  }
  iVar1 = 1;
  pfVar4 = local_4c + 4;
  pfVar2 = local_4c;
  pfVar3 = local_4c;
  do {
    pfVar2 = (float *)((int)pfVar2 + 4);
    fVar6 = *param_2;
    param_2 = param_2 + 1;
    *(char *)pfVar3 = (char)iVar1;
    *pfVar4 = fVar6;
    pfVar4 = pfVar4 + 1;
    bVar5 = iVar1 != param_3;
    *pfVar2 = ABS(fVar6);
    iVar1 = iVar1 + 1;
    pfVar3 = (float *)((int)pfVar3 + 1);
  } while (bVar5);
  if (local_4c[1] < local_4c[2]) {
    if (param_3 == 3) {
      if (local_4c[2] < local_4c[3]) {
        iVar1 = 2;
      }
      else {
        iVar1 = 1;
      }
    }
    else {
      iVar1 = 1;
    }
  }
  else {
    fVar6 = local_3c[0];
    if ((param_3 != 3) || (local_4c[3] <= local_4c[1])) goto LAB_0043bbe2;
    iVar1 = 2;
  }
  local_4c[0]._0_1_ = *(char *)((int)local_4c + iVar1);
  fVar6 = local_4c[iVar1 + 4];
LAB_0043bbe2:
  fVar7 = (float)VectorSignedToFloat(param_3,(byte)((in_fpscr & 0xfffffff) >> 0x16) & 3);
  iVar1 = param_3 << 2;
  if (ABS(fVar6) <= fVar7 * DAT_0043bc54 * ABS(fVar6)) {
    FUN_0043bb00(local_4c + 1,0,iVar1);
  }
  else {
    FUN_0043bb00(local_4c + 1,0,iVar1);
    local_4c[local_4c[0]._0_1_] = param_1 / fVar6;
  }
  *param_5 = 1;
  param_5[1] = param_3;
  fVar6 = (float)FUN_00439e90(param_4,local_4c + 1,iVar1);
  return fVar6;
}

