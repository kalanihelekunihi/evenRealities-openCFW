
float FUN_0058eac4(float param_1,int param_2,int param_3,int param_4)

{
  char cVar1;
  int iVar2;
  float *pfVar3;
  char *pcVar4;
  float *pfVar5;
  float *pfVar6;
  float *pfVar7;
  char *pcVar8;
  float *pfVar9;
  float extraout_s0;
  float extraout_s0_00;
  float fVar10;
  float fVar11;
  float fVar12;
  char local_58 [4];
  int local_54 [2];
  float local_4c [9];
  
  fVar12 = *DAT_0058ec6c;
  iVar2 = FUN_0043a0f4(*(undefined4 *)(param_2 + 0x88));
  if (iVar2 != 0) {
    return fVar12;
  }
  if (0.0 <= *(float *)(param_2 + 0x88)) {
    return fVar12;
  }
  if (*(float *)(param_2 + 0x98) == 0.0) {
    return fVar12;
  }
  FUN_00439ce0(*(undefined4 *)(param_2 + 0x8c),*(undefined1 *)(param_2 + 0xb4),param_4 + 0x324,
               param_4 + 0x1584,local_4c + 3,local_54);
  if (local_54[0] < 1) {
    if (param_3 == 0) {
      FUN_00598074(param_1 / *(float *)(param_2 + 0x88));
      goto LAB_0058ec30;
    }
  }
  else {
    pfVar7 = local_4c + 3;
    pfVar9 = local_4c;
    pfVar5 = pfVar7 + local_54[0];
    pfVar3 = pfVar9;
    pfVar6 = pfVar5;
    do {
      fVar11 = *pfVar7;
      pfVar7 = pfVar7 + 1;
      fVar10 = *pfVar6;
      pfVar6 = pfVar6 + 1;
      *pfVar3 = fVar11 + fVar10;
      pfVar3 = pfVar3 + 1;
    } while (pfVar7 != pfVar5);
    if (param_3 == 0) {
      cVar1 = FUN_00598074(param_1 / *(float *)(param_2 + 0x88));
      pfVar7 = pfVar9 + local_54[0];
      pcVar8 = local_58;
      do {
        iVar2 = (uint)(-(*pfVar9 * extraout_s0_00) < 0.0) << 0x1f;
        *pfVar9 = -(*pfVar9 * extraout_s0_00);
        pfVar9 = pfVar9 + 1;
        if (iVar2 < 0) {
          cVar1 = '\x01';
        }
        if (-1 < iVar2) {
          cVar1 = '\0';
        }
        *pcVar8 = cVar1;
        pcVar8 = pcVar8 + 1;
      } while (pfVar9 != pfVar7);
LAB_0058ec30:
      pcVar8 = local_58;
      iVar2 = local_54[0] + 1;
      if (local_54[0] < 0) {
        iVar2 = 1;
      }
      do {
        iVar2 = iVar2 + -1;
        if (iVar2 == 0) {
          return fVar12;
        }
        cVar1 = *pcVar8;
        pcVar8 = pcVar8 + 1;
      } while (cVar1 != '\0');
      return local_4c[0] + DAT_0058ec70;
    }
  }
  fVar10 = (*(float *)(param_2 + 0x90) - *(float *)(param_2 + 0xa0)) / *(float *)(param_2 + 0x98);
  if (((-1 < (int)((uint)(fVar10 < 0.0) << 0x1f)) && (fVar10 != 0.0)) &&
     (fVar10 = (1.0 - *(float *)(param_2 + 0x90)) / fVar10, -1 < (int)((uint)(fVar10 < 0.0) << 0x1f)
     )) {
    cVar1 = FUN_00598074(param_1 / *(float *)(param_2 + 0x88));
    pcVar8 = local_58;
    if (0 < local_54[0]) {
      pfVar7 = local_4c;
      pfVar9 = pfVar7 + local_54[0];
      pcVar4 = pcVar8;
      do {
        iVar2 = (uint)(-(*pfVar7 * extraout_s0) < 0.0) << 0x1f;
        *pfVar7 = -(*pfVar7 * extraout_s0);
        pfVar7 = pfVar7 + 1;
        if (iVar2 < 0) {
          cVar1 = '\x01';
        }
        if (-1 < iVar2) {
          cVar1 = '\0';
        }
        *pcVar4 = cVar1;
        pcVar4 = pcVar4 + 1;
      } while (pfVar9 != pfVar7);
    }
    iVar2 = local_54[0] + 1;
    if (local_54[0] < 0) {
      iVar2 = 1;
    }
    do {
      iVar2 = iVar2 + -1;
      if (iVar2 == 0) {
        return fVar12;
      }
      cVar1 = *pcVar8;
      pcVar8 = pcVar8 + 1;
    } while (cVar1 != '\0');
    fVar12 = fVar10 + local_4c[0];
  }
  return fVar12;
}

