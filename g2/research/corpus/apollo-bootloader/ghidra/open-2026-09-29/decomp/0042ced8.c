
undefined4 state_range_update_42ced8(float *param_1)

{
  float fVar1;
  byte bVar2;
  
  fVar1 = DAT_0042d0f4;
  if ((-1 < (int)((uint)(*param_1 < DAT_0042d0f4) << 0x1f)) || (*param_1 < DAT_0042d0f8)) {
    if ((*param_1 < DAT_0042d0f4) || (-1 < (int)((uint)(*param_1 < DAT_0042d0fc) << 0x1f))) {
      if ((*param_1 < DAT_0042d0fc) || (-1 < (int)((uint)(*param_1 < DAT_0042d100) << 0x1f))) {
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
    if (*DAT_0042d7c4 == '\0') {
      *DAT_0042d7c8 = 0;
    }
    state_update_critical_42cea4(0);
    param_1[1] = DAT_0042d0f8;
    param_1[2] = fVar1;
  }
  else if (bVar2 == 2) {
    if (*DAT_0042d7c4 == '\0') {
      *DAT_0042d7c8 = 1;
    }
    state_update_critical_42cea4(2);
    param_1[1] = DAT_0042d7d0;
    param_1[2] = DAT_0042d100;
  }
  else {
    if (1 < bVar2) {
      param_1[1] = 0.0;
      param_1[2] = 0.0;
      return 1;
    }
    if (*DAT_0042d7c4 == '\0') {
      *DAT_0042d7c8 = 0;
    }
    state_update_critical_42cea4(1);
    param_1[1] = DAT_0042d7cc;
    param_1[2] = DAT_0042d0fc;
  }
  return 0;
}

