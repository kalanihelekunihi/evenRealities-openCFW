
undefined4 FUN_005a0a70(float param_1)

{
  undefined4 uVar1;
  
  if ((-1 < (int)((uint)(param_1 < -20.0) << 0x1f)) || (param_1 < DAT_005a0c1c)) {
    if ((param_1 < -20.0) || (-1 < (int)((uint)(param_1 < 0.0) << 0x1f))) {
      if ((param_1 < 0.0) || (-1 < (int)((uint)(param_1 < DAT_005a0d40) << 0x1f))) {
        if ((param_1 < DAT_005a0d40) || (-1 < (int)((uint)(param_1 < DAT_005a0d98) << 0x1f))) {
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

