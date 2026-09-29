
float ldexpf(float param_1,uint param_2)

{
  uint uVar1;
  uint in_fpscr;
  
  uVar1 = (uint)ABS(param_1) >> 0x17;
  if (-1 < (int)param_2) {
    if (uVar1 == 0) {
      if (ABS(param_1) == 0.0) {
        return param_1;
      }
      if (param_2 < 0x80) {
        return param_1;
      }
      param_1 = param_1 * 1.7014118e+38;
      param_2 = param_2 - 0x7f;
      uVar1 = (uint)ABS(param_1) >> 0x17;
    }
    else if (uVar1 == 0xff) {
      return param_1;
    }
    if (uVar1 + param_2 < 0xff) {
      return param_1;
    }
    *DAT_00439cd4 = 0x22;
    return param_1;
  }
  param_2 = -param_2;
  if (uVar1 == 0) {
    if (ABS(param_1) == 0.0) {
      return param_1;
    }
  }
  else {
    if (uVar1 == 0xff) {
      return param_1;
    }
    if (param_2 < uVar1) {
      return param_1;
    }
    param_2 = param_2 - (uVar1 - 1);
    param_1 = (float)((int)param_1 + (uVar1 - 1) * -0x800000);
  }
  if (0x19 < param_2) {
    return (float)((uint)param_1 & 0x80000000);
  }
  return (float)((in_fpscr & 0xffffe0e0) >> 4);
}

