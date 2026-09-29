
undefined4
FUN_005177a4(undefined4 param_1,float param_2,undefined4 param_3,float param_4,float *param_5,
            float *param_6)

{
  int iVar1;
  undefined4 uVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  
  uVar2 = 0;
  fVar3 = *param_5;
  iVar1 = (uint)(fVar3 < 0.0) << 0x1f;
  if (iVar1 < 0) {
    param_2 = -fVar3;
  }
  if (-1 < iVar1) {
    param_2 = fVar3;
  }
  fVar4 = *param_6;
  iVar1 = (uint)(fVar4 < 0.0) << 0x1f;
  if (iVar1 < 0) {
    param_4 = -fVar4;
  }
  if (-1 < iVar1) {
    param_4 = fVar4;
  }
  if (-1 < (int)((uint)(param_2 < param_4) << 0x1f)) {
    param_2 = param_4;
  }
  fVar5 = fVar3 - fVar4;
  if ((int)((uint)(fVar5 < 0.0) << 0x1f) < 0) {
    fVar5 = fVar4 - fVar3;
  }
  if (fVar5 <= param_2 * DAT_00517854) {
    fVar3 = ABS(param_5[1]);
    if (-1 < (int)((uint)(ABS(param_5[1]) < ABS(param_6[1])) << 0x1f)) {
      fVar3 = ABS(param_6[1]);
    }
    fVar4 = param_5[1] - param_6[1];
    if ((int)((uint)(fVar4 < 0.0) << 0x1f) < 0) {
      fVar4 = param_6[1] - param_5[1];
    }
    if (fVar4 <= fVar3 * DAT_00517854) {
      uVar2 = 1;
    }
  }
  return uVar2;
}

