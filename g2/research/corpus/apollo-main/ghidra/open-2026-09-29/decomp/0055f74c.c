
undefined4 FUN_0055f74c(undefined4 param_1,float *param_2)

{
  float fVar1;
  
  switch(param_1) {
  case 0:
    DAT_0055f844[1] = 1;
    return 0;
  case 1:
    DAT_0055f844[1] = 0;
    break;
  case 2:
    if (param_2 == (float *)0x0) {
      return 0xffffffea;
    }
    if (5 < *(byte *)param_2) {
      return 0xffffffea;
    }
    *DAT_0055f844 = *(byte *)param_2;
    break;
  case 3:
    if (param_2 == (float *)0x0) {
      return 0xffffffea;
    }
    fVar1 = *param_2;
    if (NAN(fVar1)) {
      return 0xffffffea;
    }
    if ((int)fVar1 < 0) {
      return 0xffffffea;
    }
    if (fVar1 == 0.0) {
      return 0xffffffea;
    }
    *(float *)(DAT_0055f844 + 4) = fVar1;
    break;
  case 4:
    if (param_2 == (float *)0x0) {
      return 0xffffffea;
    }
    fVar1 = *param_2;
    if (NAN(fVar1)) {
      return 0xffffffea;
    }
    if ((int)fVar1 < 0) {
      return 0xffffffea;
    }
    if (fVar1 == 0.0) {
      return 0xffffffea;
    }
    *(float *)(DAT_0055f844 + 8) = fVar1;
    break;
  case 5:
    if (param_2 == (float *)0x0) {
      return 0xffffffea;
    }
    fVar1 = *param_2;
    if (fVar1 == 0.0) {
      return 0xffffffea;
    }
    if (-1 < (int)fVar1) {
      fVar1 = -fVar1;
    }
    *(float *)(DAT_0055f844 + 0xc) = fVar1;
    break;
  case 6:
    if (param_2 == (float *)0x0) {
      return 0xffffffea;
    }
    fVar1 = *param_2;
    if (fVar1 == 0.0) {
      return 0xffffffea;
    }
    if ((int)fVar1 < 0) {
      *(float *)(DAT_0055f844 + 0x10) = fVar1;
    }
    else {
      *(float *)(DAT_0055f844 + 0x10) = -fVar1;
    }
    break;
  default:
    return 0xffffffea;
  }
  return 0;
}

