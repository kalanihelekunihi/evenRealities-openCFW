
undefined4 FUN_005a1e8c(float param_1)

{
  undefined4 uVar1;
  
  if ((-1 < (int)((uint)(param_1 < -20.0) << 0x1f)) || (param_1 < DAT_005a20dc)) {
    if ((param_1 < -20.0) || (-1 < (int)((uint)(param_1 < 0.0) << 0x1f))) {
      if ((param_1 < 0.0) || (-1 < (int)((uint)(param_1 < DAT_005a20e0) << 0x1f))) {
        if ((param_1 < DAT_005a20e0) || (-1 < (int)((uint)(param_1 < DAT_005a20e4) << 0x1f))) {
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

