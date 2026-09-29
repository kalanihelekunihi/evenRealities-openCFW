
void FUN_004f9d84(int param_1,int param_2,int param_3)

{
  int iVar1;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004fa710,DAT_004fa400,DAT_004fa724,0xfc2,DAT_004fa720,param_1,param_2,param_3
                 ,*DAT_004fa04c);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x11000000,DAT_004fa728,DAT_004fa728,param_1,param_2,param_3,*DAT_004fa04c);
  }
  if (param_1 == -1) {
    param_3 = (uint)*DAT_004fa04c - param_3;
    if ((param_3 < 0) || ((int)(uint)*DAT_004fa04c <= param_3)) {
      if (*DAT_004fa04c == 0) {
        *DAT_004faa2c = -1;
      }
      else {
        *DAT_004faa2c = *DAT_004fa04c - 1;
      }
    }
    else {
      *DAT_004faa2c = param_3;
    }
  }
  else if (param_1 == -2) {
    if (*DAT_004fa04c == 0) {
      if (*DAT_004fa04c == 0) {
        *DAT_004faa2c = -2;
      }
      else {
        *DAT_004faa2c = 0;
      }
    }
    else {
      *DAT_004faa2c = 0;
    }
  }
  else if (param_1 < 0) {
    if (*DAT_004fa04c == 0) {
      *DAT_004faa2c = -1;
    }
    else {
      *DAT_004faa2c = 0;
    }
  }
  else {
    param_1 = param_1 - param_2;
    if ((param_1 < 0) || ((int)(uint)*DAT_004fa04c <= param_1)) {
      if (*DAT_004fa04c == 0) {
        *DAT_004faa2c = -1;
      }
      else {
        *DAT_004faa2c = 0;
      }
    }
    else {
      *DAT_004faa2c = param_1;
    }
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004fa710,DAT_004fa400,DAT_004fa724,0xfef,DAT_004faa30,*DAT_004faa2c);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004faa34,DAT_004faa34,*DAT_004faa2c);
  }
  return;
}

