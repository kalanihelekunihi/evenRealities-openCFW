
undefined4 spotmgr_temperature_range_42ad40(float param_1)

{
  undefined4 uVar1;
  
  if ((-1 < (int)((uint)(param_1 < -20.0) << 0x1f)) || (param_1 < DAT_0042aeec)) {
    if ((param_1 < -20.0) || (-1 < (int)((uint)(param_1 < 0.0) << 0x1f))) {
      if ((param_1 < 0.0) || (-1 < (int)((uint)(param_1 < DAT_0042b010) << 0x1f))) {
        if ((param_1 < DAT_0042b010) || (-1 < (int)((uint)(param_1 < DAT_0042b068) << 0x1f))) {
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

