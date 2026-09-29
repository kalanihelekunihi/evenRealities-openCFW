
undefined4 float_range_classify_427e0c(float param_1)

{
  undefined4 uVar1;
  
  if ((-1 < (int)((uint)(param_1 < -20.0) << 0x1f)) || (param_1 < DAT_0042805c)) {
    if ((param_1 < -20.0) || (-1 < (int)((uint)(param_1 < 0.0) << 0x1f))) {
      if ((param_1 < 0.0) || (-1 < (int)((uint)(param_1 < DAT_00428060) << 0x1f))) {
        if ((param_1 < DAT_00428060) || (-1 < (int)((uint)(param_1 < DAT_00428064) << 0x1f))) {
          uVar1 = 4;
        }
        else {
          uVar1 = 3;
        }
      }
      else {
        uVar1 = 2;
      }
    }
    else {
      uVar1 = 1;
    }
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

