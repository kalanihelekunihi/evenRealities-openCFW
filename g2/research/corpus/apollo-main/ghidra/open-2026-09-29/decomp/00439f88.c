
float FUN_00439f88(float param_1,float param_2)

{
  bool bVar1;
  
  bVar1 = 0.0 <= param_2;
  if (!NAN(param_2)) {
    if (param_2 == 0.0) {
      bVar1 = CARRY4((uint)param_1,(uint)param_1);
    }
    if (param_2 == 0.0 && ABS(param_1) == 0.0) {
      if (bVar1) {
        param_1 = param_2;
      }
      return param_1;
    }
    if (param_1 < param_2) {
      param_1 = param_2;
    }
  }
  return param_1;
}

