
uint FUN_005640e4(float param_1,float param_2,float param_3,float param_4,float *param_5)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  
  fVar7 = DAT_00564158;
  iVar3 = *DAT_00564a40;
  fVar4 = param_3 - param_1;
  fVar6 = *(float *)(iVar3 + 0x30);
  fVar5 = param_4 - param_2;
  fVar9 = *(float *)(iVar3 + 0x34) - fVar6;
  fVar12 = fVar4 * (fVar6 - fVar6) - fVar9 * fVar5;
  fVar8 = ((param_2 - fVar6) * fVar4 + (fVar6 - param_1) * fVar5) / fVar12;
  uVar2 = 0;
  fVar12 = ((param_2 - fVar6) * fVar9 + (fVar6 - param_1) * (fVar6 - fVar6)) / fVar12;
  if ((((0.0 <= fVar8) && ((int)((uint)(fVar8 < DAT_00564158) << 0x1f) < 0)) && (0.0 <= fVar12)) &&
     ((int)((uint)(fVar12 < DAT_00564158) << 0x1f) < 0)) {
    *param_5 = param_1 + fVar12 * fVar4;
    fVar6 = param_2 + fVar12 * fVar5;
    param_5[1] = fVar6;
    fVar9 = *param_5;
    iVar1 = (uint)(fVar9 < 0.0) << 0x1f;
    if (iVar1 < 0) {
      fVar8 = -fVar9;
    }
    if (-1 < iVar1) {
      fVar8 = fVar9;
    }
    fVar12 = ABS(param_1);
    if (-1 < (int)((uint)(ABS(param_1) < fVar8) << 0x1f)) {
      fVar12 = fVar8;
    }
    fVar10 = param_1 - fVar9;
    if ((int)((uint)(fVar10 < 0.0) << 0x1f) < 0) {
      fVar10 = fVar9 - param_1;
    }
    if (fVar10 <= fVar12 * DAT_00564558) {
      fVar12 = ABS(param_2);
      if (-1 < (int)((uint)(ABS(param_2) < ABS(param_5[1])) << 0x1f)) {
        fVar12 = ABS(param_5[1]);
      }
      fVar10 = param_2 - fVar6;
      if ((int)((uint)(fVar10 < 0.0) << 0x1f) < 0) {
        fVar10 = fVar6 - param_2;
      }
      if (fVar10 <= fVar12 * DAT_00564558) goto LAB_0056428c;
    }
    if ((int)((uint)(ABS(param_3) < fVar8) << 0x1f) < 0) {
      fVar8 = ABS(param_3);
    }
    fVar12 = param_3 - fVar9;
    if ((int)((uint)(fVar12 < 0.0) << 0x1f) < 0) {
      fVar12 = fVar9 - param_3;
    }
    if (fVar12 <= fVar8 * DAT_00564558) {
      fVar8 = ABS(param_4);
      if (-1 < (int)((uint)(ABS(param_4) < ABS(param_5[1])) << 0x1f)) {
        fVar8 = ABS(param_5[1]);
      }
      fVar9 = param_4 - fVar6;
      if ((int)((uint)(fVar9 < 0.0) << 0x1f) < 0) {
        fVar9 = fVar6 - param_4;
      }
      if (fVar9 <= fVar8 * DAT_00564558) goto LAB_0056428c;
    }
    uVar2 = 1;
  }
LAB_0056428c:
  fVar8 = DAT_00564558;
  fVar12 = *(float *)(iVar3 + 0x34);
  fVar9 = fVar12 - fVar12;
  fVar6 = param_2 - fVar12;
  fVar12 = fVar12 - *(float *)(iVar3 + 0x30);
  fVar11 = *(float *)(iVar3 + 0x30) - param_1;
  fVar13 = fVar4 * fVar9 - fVar12 * fVar5;
  fVar10 = (fVar6 * fVar4 + fVar11 * fVar5) / fVar13;
  fVar13 = (fVar6 * fVar12 + fVar11 * fVar9) / fVar13;
  if (((0.0 <= fVar10) && ((int)((uint)(fVar10 < fVar7) << 0x1f) < 0)) &&
     ((0.0 <= fVar13 && ((int)((uint)(fVar13 < fVar7) << 0x1f) < 0)))) {
    if (uVar2 == 1) {
      fVar12 = *param_5;
      iVar1 = (uint)(fVar12 < 0.0) << 0x1f;
      if (iVar1 < 0) {
        fVar9 = -fVar12;
      }
      if (-1 < iVar1) {
        fVar9 = fVar12;
      }
      fVar10 = param_1 + fVar13 * fVar4;
      iVar1 = (uint)(fVar10 < 0.0) << 0x1f;
      if (iVar1 < 0) {
        fVar6 = -fVar10;
      }
      if (-1 < iVar1) {
        fVar6 = fVar10;
      }
      if (-1 < (int)((uint)(fVar9 < fVar6) << 0x1f)) {
        fVar9 = fVar6;
      }
      fVar6 = fVar12 - fVar10;
      if ((int)((uint)(fVar6 < 0.0) << 0x1f) < 0) {
        fVar6 = fVar10 - fVar12;
      }
      if (fVar6 <= fVar9 * DAT_00564558) {
        fVar9 = param_2 + fVar13 * fVar5;
        iVar1 = (uint)(fVar9 < 0.0) << 0x1f;
        if (iVar1 < 0) {
          fVar6 = -fVar9;
        }
        if (-1 < iVar1) {
          fVar6 = fVar9;
        }
        fVar12 = ABS(param_5[1]);
        if (-1 < (int)((uint)(ABS(param_5[1]) < fVar6) << 0x1f)) {
          fVar12 = fVar6;
        }
        fVar6 = param_5[1] - fVar9;
        if ((int)((uint)(fVar6 < 0.0) << 0x1f) < 0) {
          fVar6 = fVar9 - param_5[1];
        }
        if (fVar6 <= fVar12 * DAT_00564558) goto LAB_005644d2;
      }
    }
    param_5[uVar2 * 2] = param_1 + fVar13 * fVar4;
    param_5[uVar2 * 2 + 1] = param_2 + fVar13 * fVar5;
    fVar9 = *param_5;
    iVar1 = (uint)(fVar9 < 0.0) << 0x1f;
    fVar6 = fVar4;
    if (iVar1 < 0) {
      fVar6 = -fVar9;
    }
    if (-1 < iVar1) {
      fVar6 = fVar9;
    }
    fVar12 = ABS(param_1);
    if (-1 < (int)((uint)(ABS(param_1) < fVar6) << 0x1f)) {
      fVar12 = fVar6;
    }
    fVar10 = param_1 - fVar9;
    if ((int)((uint)(fVar10 < 0.0) << 0x1f) < 0) {
      fVar10 = fVar9 - param_1;
    }
    if (fVar10 <= fVar12 * fVar8) {
      fVar12 = ABS(param_2);
      if (-1 < (int)((uint)(ABS(param_2) < ABS(param_5[1])) << 0x1f)) {
        fVar12 = ABS(param_5[1]);
      }
      fVar10 = param_2 - param_5[1];
      if ((int)((uint)(fVar10 < 0.0) << 0x1f) < 0) {
        fVar10 = param_5[1] - param_2;
      }
      if (fVar10 <= fVar12 * fVar8) goto LAB_005644d2;
    }
    if ((int)((uint)(ABS(param_3) < fVar6) << 0x1f) < 0) {
      fVar6 = ABS(param_3);
    }
    fVar12 = param_3 - fVar9;
    if ((int)((uint)(fVar12 < 0.0) << 0x1f) < 0) {
      fVar12 = fVar9 - param_3;
    }
    if (fVar12 <= fVar6 * fVar8) {
      fVar6 = ABS(param_4);
      if (-1 < (int)((uint)(ABS(param_4) < ABS(param_5[1])) << 0x1f)) {
        fVar6 = ABS(param_5[1]);
      }
      fVar9 = param_4 - param_5[1];
      if ((int)((uint)(fVar9 < 0.0) << 0x1f) < 0) {
        fVar9 = param_5[1] - param_4;
      }
      if (fVar9 <= fVar6 * fVar8) goto LAB_005644d2;
    }
    uVar2 = uVar2 + 1;
  }
LAB_005644d2:
  fVar8 = DAT_00564558;
  fVar12 = *(float *)(iVar3 + 0x30);
  fVar11 = *(float *)(iVar3 + 0x34) - fVar12;
  fVar6 = param_2 - fVar12;
  fVar9 = fVar4 * fVar11 - (fVar12 - fVar12) * fVar5;
  fVar10 = (fVar6 * fVar4 + (fVar12 - param_1) * fVar5) / fVar9;
  fVar12 = (fVar6 * (fVar12 - fVar12) + (fVar12 - param_1) * fVar11) / fVar9;
  if (((0.0 <= fVar10) && ((int)((uint)(fVar10 < fVar7) << 0x1f) < 0)) &&
     ((0.0 <= fVar12 && (((int)((uint)(fVar12 < fVar7) << 0x1f) < 0 && (uVar2 < 2)))))) {
    if (uVar2 == 1) {
      fVar10 = *param_5;
      iVar1 = (uint)(fVar10 < 0.0) << 0x1f;
      if (iVar1 < 0) {
        fVar9 = -fVar10;
      }
      if (-1 < iVar1) {
        fVar9 = fVar10;
      }
      fVar11 = param_1 + fVar12 * fVar4;
      iVar1 = (uint)(fVar11 < 0.0) << 0x1f;
      if (iVar1 < 0) {
        fVar6 = -fVar11;
      }
      if (-1 < iVar1) {
        fVar6 = fVar11;
      }
      if (-1 < (int)((uint)(fVar9 < fVar6) << 0x1f)) {
        fVar9 = fVar6;
      }
      fVar6 = fVar10 - fVar11;
      if ((int)((uint)(fVar6 < 0.0) << 0x1f) < 0) {
        fVar6 = fVar11 - fVar10;
      }
      if (fVar6 <= fVar9 * DAT_00564558) {
        fVar9 = param_2 + fVar12 * fVar5;
        iVar1 = (uint)(fVar9 < 0.0) << 0x1f;
        if (iVar1 < 0) {
          fVar6 = -fVar9;
        }
        if (-1 < iVar1) {
          fVar6 = fVar9;
        }
        fVar10 = ABS(param_5[1]);
        if (-1 < (int)((uint)(ABS(param_5[1]) < fVar6) << 0x1f)) {
          fVar10 = fVar6;
        }
        fVar6 = param_5[1] - fVar9;
        if ((int)((uint)(fVar6 < 0.0) << 0x1f) < 0) {
          fVar6 = fVar9 - param_5[1];
        }
        if (fVar6 <= fVar10 * DAT_00564558) goto LAB_00564724;
      }
    }
    param_5[uVar2 * 2] = param_1 + fVar12 * fVar4;
    param_5[uVar2 * 2 + 1] = param_2 + fVar12 * fVar5;
    fVar9 = *param_5;
    iVar1 = (uint)(fVar9 < 0.0) << 0x1f;
    fVar6 = fVar4;
    if (iVar1 < 0) {
      fVar6 = -fVar9;
    }
    if (-1 < iVar1) {
      fVar6 = fVar9;
    }
    fVar12 = ABS(param_1);
    if (-1 < (int)((uint)(ABS(param_1) < fVar6) << 0x1f)) {
      fVar12 = fVar6;
    }
    fVar10 = param_1 - fVar9;
    if ((int)((uint)(fVar10 < 0.0) << 0x1f) < 0) {
      fVar10 = fVar9 - param_1;
    }
    if (fVar10 <= fVar12 * fVar8) {
      fVar12 = ABS(param_2);
      if (-1 < (int)((uint)(ABS(param_2) < ABS(param_5[1])) << 0x1f)) {
        fVar12 = ABS(param_5[1]);
      }
      fVar10 = param_2 - param_5[1];
      if ((int)((uint)(fVar10 < 0.0) << 0x1f) < 0) {
        fVar10 = param_5[1] - param_2;
      }
      if (fVar10 <= fVar12 * fVar8) goto LAB_00564724;
    }
    if ((int)((uint)(ABS(param_3) < fVar6) << 0x1f) < 0) {
      fVar6 = ABS(param_3);
    }
    fVar12 = param_3 - fVar9;
    if ((int)((uint)(fVar12 < 0.0) << 0x1f) < 0) {
      fVar12 = fVar9 - param_3;
    }
    if (fVar12 <= fVar6 * fVar8) {
      fVar6 = ABS(param_4);
      if (-1 < (int)((uint)(ABS(param_4) < ABS(param_5[1])) << 0x1f)) {
        fVar6 = ABS(param_5[1]);
      }
      fVar9 = param_4 - param_5[1];
      if ((int)((uint)(fVar9 < 0.0) << 0x1f) < 0) {
        fVar9 = param_5[1] - param_4;
      }
      if (fVar9 <= fVar6 * fVar8) goto LAB_00564724;
    }
    uVar2 = uVar2 + 1;
  }
LAB_00564724:
  fVar8 = DAT_00564970;
  fVar6 = *(float *)(iVar3 + 0x34);
  fVar10 = fVar6 - *(float *)(iVar3 + 0x30);
  fVar11 = param_2 - *(float *)(iVar3 + 0x30);
  fVar9 = fVar4 * fVar10 - (fVar6 - fVar6) * fVar5;
  fVar12 = (fVar11 * fVar4 + (fVar6 - param_1) * fVar5) / fVar9;
  fVar6 = fVar11 * (fVar6 - fVar6) + (fVar6 - param_1) * fVar10;
  fVar10 = fVar6 / fVar9;
  if ((((0.0 <= fVar12) && ((int)((uint)(fVar12 < fVar7) << 0x1f) < 0)) && (0.0 <= fVar10)) &&
     (((int)((uint)(fVar10 < fVar7) << 0x1f) < 0 && (uVar2 < 2)))) {
    if (uVar2 == 1) {
      fVar7 = *param_5;
      iVar3 = (uint)(fVar7 < 0.0) << 0x1f;
      if (iVar3 < 0) {
        fVar6 = -fVar7;
      }
      if (-1 < iVar3) {
        fVar6 = fVar7;
      }
      fVar12 = param_1 + fVar10 * fVar4;
      iVar3 = (uint)(fVar12 < 0.0) << 0x1f;
      if (iVar3 < 0) {
        fVar9 = -fVar12;
      }
      if (-1 < iVar3) {
        fVar9 = fVar12;
      }
      if (-1 < (int)((uint)(fVar6 < fVar9) << 0x1f)) {
        fVar6 = fVar9;
      }
      fVar9 = fVar7 - fVar12;
      if ((int)((uint)(fVar9 < 0.0) << 0x1f) < 0) {
        fVar9 = fVar12 - fVar7;
      }
      if (fVar9 <= fVar6 * DAT_00564970) {
        fVar7 = param_2 + fVar10 * fVar5;
        iVar3 = (uint)(fVar7 < 0.0) << 0x1f;
        if (iVar3 < 0) {
          fVar9 = -fVar7;
        }
        if (-1 < iVar3) {
          fVar9 = fVar7;
        }
        fVar6 = ABS(param_5[1]);
        if (-1 < (int)((uint)(ABS(param_5[1]) < fVar9) << 0x1f)) {
          fVar6 = fVar9;
        }
        fVar9 = param_5[1] - fVar7;
        if ((int)((uint)(fVar9 < 0.0) << 0x1f) < 0) {
          fVar9 = fVar7 - param_5[1];
        }
        if (fVar9 <= fVar6 * DAT_00564970) {
          return 1;
        }
      }
    }
    param_5[uVar2 * 2] = param_1 + fVar10 * fVar4;
    fVar7 = param_2 + fVar10 * fVar5;
    param_5[uVar2 * 2 + 1] = fVar7;
    fVar4 = *param_5;
    iVar3 = (uint)(fVar4 < 0.0) << 0x1f;
    if (iVar3 < 0) {
      fVar7 = -fVar4;
    }
    if (-1 < iVar3) {
      fVar7 = fVar4;
    }
    fVar5 = ABS(param_1);
    if (-1 < (int)((uint)(ABS(param_1) < fVar7) << 0x1f)) {
      fVar5 = fVar7;
    }
    fVar6 = param_1 - fVar4;
    if ((int)((uint)(fVar6 < 0.0) << 0x1f) < 0) {
      fVar6 = fVar4 - param_1;
    }
    if (fVar6 <= fVar5 * fVar8) {
      fVar5 = ABS(param_2);
      if (-1 < (int)((uint)(ABS(param_2) < ABS(param_5[1])) << 0x1f)) {
        fVar5 = ABS(param_5[1]);
      }
      fVar6 = param_2 - param_5[1];
      if ((int)((uint)(fVar6 < 0.0) << 0x1f) < 0) {
        fVar6 = param_5[1] - param_2;
      }
      if (fVar6 <= fVar5 * fVar8) {
        return uVar2;
      }
    }
    if ((int)((uint)(ABS(param_3) < fVar7) << 0x1f) < 0) {
      fVar7 = ABS(param_3);
    }
    fVar5 = param_3 - fVar4;
    if ((int)((uint)(fVar5 < 0.0) << 0x1f) < 0) {
      fVar5 = fVar4 - param_3;
    }
    if (fVar5 <= fVar7 * fVar8) {
      fVar7 = ABS(param_4);
      if (-1 < (int)((uint)(ABS(param_4) < ABS(param_5[1])) << 0x1f)) {
        fVar7 = ABS(param_5[1]);
      }
      fVar4 = param_4 - param_5[1];
      if ((int)((uint)(fVar4 < 0.0) << 0x1f) < 0) {
        fVar4 = param_5[1] - param_4;
      }
      if (fVar4 <= fVar7 * fVar8) {
        return uVar2;
      }
    }
    uVar2 = uVar2 + 1;
  }
  return uVar2;
}

