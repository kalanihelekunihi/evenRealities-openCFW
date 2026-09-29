
undefined4 FUN_005a00fc(float *param_1)

{
  float fVar1;
  byte bVar2;
  
  fVar1 = DAT_005a0318;
  if ((-1 < (int)((uint)(*param_1 < DAT_005a0318) << 0x1f)) || (*param_1 < DAT_005a031c)) {
    if ((*param_1 < DAT_005a0318) || (-1 < (int)((uint)(*param_1 < DAT_005a0320) << 0x1f))) {
      if ((*param_1 < DAT_005a0320) || (-1 < (int)((uint)(*param_1 < DAT_005a0324) << 0x1f))) {
        bVar2 = 3;
      }
      else {
        bVar2 = 2;
      }
    }
    else {
      bVar2 = 1;
    }
  }
  else {
    bVar2 = 0;
  }
  if (bVar2 == 0) {
    if (*DAT_005a09e8 == '\0') {
      *DAT_005a09ec = 0;
    }
    FUN_005a00c8(0);
    param_1[1] = DAT_005a031c;
    param_1[2] = fVar1;
  }
  else if (bVar2 == 2) {
    if (*DAT_005a09e8 == '\0') {
      *DAT_005a09ec = 1;
    }
    FUN_005a00c8(2);
    param_1[1] = DAT_005a09f4;
    param_1[2] = DAT_005a0324;
  }
  else {
    if (1 < bVar2) {
      param_1[1] = 0.0;
      param_1[2] = 0.0;
      return 1;
    }
    if (*DAT_005a09e8 == '\0') {
      *DAT_005a09ec = 0;
    }
    FUN_005a00c8(1);
    param_1[1] = DAT_005a09f0;
    param_1[2] = DAT_005a0320;
  }
  return 0;
}

