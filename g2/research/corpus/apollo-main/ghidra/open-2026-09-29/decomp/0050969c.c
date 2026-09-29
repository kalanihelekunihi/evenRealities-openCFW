
float FUN_0050969c(float param_1,float param_2)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  bool bVar4;
  float fVar5;
  float fVar6;
  
  uVar1 = -((int)param_1 >> 0x1f);
  uVar2 = (int)param_1 * 2;
  uVar3 = (int)param_2 * 2;
  if (((uint)param_2 & 0x80000000) != 0) {
    uVar1 = uVar1 + 0xc;
  }
  if (uVar2 < 0xff000000 && uVar3 < 0xff000000) {
    if (uVar3 < uVar2) {
      uVar1 = uVar1 ^ 4;
    }
    fVar5 = 0.0;
    if (uVar3 != 0) {
      if (uVar3 < uVar2) {
        fVar5 = ABS(param_2) / ABS(param_1);
      }
      else {
        fVar5 = ABS(param_1) / ABS(param_2);
      }
    }
  }
  else {
    bVar4 = uVar2 == 0xff000000;
    if (bVar4) {
      uVar1 = uVar1 ^ 4;
    }
    if (uVar2 < 0xff000001) {
      bVar4 = uVar3 == 0xff000000;
      uVar2 = uVar3;
    }
    if (0xfeffffff < uVar2 && !bVar4) {
      return NAN;
    }
    if (uVar3 + (int)param_1 * -2 == 0) {
      fVar5 = 1.0;
    }
    else {
      fVar5 = 0.0;
    }
  }
  if (0x3e8930a3 < (int)fVar5) {
    fVar5 = (DAT_0055ea1c + DAT_0055ea08 * fVar5) / (DAT_0055ea08 + fVar5);
    uVar1 = uVar1 | 2;
  }
  if (0x72ffffff < (uint)((int)fVar5 * 2)) {
    fVar6 = fVar5 * fVar5;
    fVar5 = (fVar5 + fVar5 * fVar6 * DAT_0055ea0c) /
            (DAT_0055ea18 + (DAT_0055ea14 + DAT_0055ea10 * fVar6) * fVar6);
  }
  if ((uVar1 >> 1 & 2) != 0) {
    fVar5 = -fVar5;
  }
  fVar5 = fVar5 + *(float *)(&DAT_0055ea20 + (uVar1 >> 1) * 4);
  if ((uVar1 & 1) != 0) {
    fVar5 = -fVar5;
  }
  return fVar5;
}

