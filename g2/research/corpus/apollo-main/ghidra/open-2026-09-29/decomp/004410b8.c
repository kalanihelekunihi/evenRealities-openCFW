
undefined4 FUN_004410b8(byte *param_1)

{
  undefined4 unaff_r7;
  
  if (param_1[3] != 0xff) {
    if (param_1[3] == 0) {
      FUN_00440f38(param_1,4);
    }
    else {
      param_1[2] = (byte)((uint)param_1[3] * (uint)param_1[2] >> 8);
      param_1[1] = (byte)((uint)param_1[3] * (uint)param_1[1] >> 8);
      *param_1 = (byte)((uint)param_1[3] * (uint)*param_1 >> 8);
    }
  }
  return unaff_r7;
}

