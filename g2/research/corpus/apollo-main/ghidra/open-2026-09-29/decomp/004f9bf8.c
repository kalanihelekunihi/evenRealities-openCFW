
void FUN_004f9bf8(int param_1,undefined4 param_2,int param_3)

{
  int iVar1;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004fa710,DAT_004fa400,DAT_004fa70c,0xf8b,DAT_004fa708,param_1,param_2,param_3
                 ,*DAT_004fa04c);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x11000000,DAT_004fa714,DAT_004fa714,param_1,param_2,param_3,*DAT_004fa04c);
  }
  if (param_1 == -1) {
    param_3 = (uint)*DAT_004fa04c - param_3;
    if ((param_3 < 0) || ((int)(uint)*DAT_004fa04c <= param_3)) {
      if (*DAT_004fa04c == 0) {
        *DAT_004f9d78 = -1;
      }
      else {
        *DAT_004f9d78 = *DAT_004fa04c - 1;
      }
    }
    else {
      *DAT_004f9d78 = param_3;
    }
  }
  else if (param_1 == -2) {
    param_3 = param_3 + -1;
    if ((param_3 < 0) || ((int)(uint)*DAT_004fa04c <= param_3)) {
      if (*DAT_004fa04c == 0) {
        *DAT_004f9d78 = -2;
      }
      else {
        *DAT_004f9d78 = 0;
      }
    }
    else {
      *DAT_004f9d78 = param_3;
    }
  }
  else if (param_1 < 0) {
    if (*DAT_004fa04c == 0) {
      *DAT_004f9d78 = -1;
    }
    else {
      *DAT_004f9d78 = 0;
    }
  }
  else {
    param_3 = param_3 + param_1;
    if ((param_3 < 0) || ((int)(uint)*DAT_004fa04c <= param_3)) {
      if (*DAT_004fa04c == 0) {
        *DAT_004f9d78 = -1;
      }
      else {
        *DAT_004f9d78 = 0;
      }
    }
    else {
      *DAT_004f9d78 = param_3;
    }
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004fa710,DAT_004fa400,DAT_004fa70c,0xfb9,DAT_004fa718,*DAT_004f9d78);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004fa71c,DAT_004fa71c,*DAT_004f9d78);
  }
  return;
}

