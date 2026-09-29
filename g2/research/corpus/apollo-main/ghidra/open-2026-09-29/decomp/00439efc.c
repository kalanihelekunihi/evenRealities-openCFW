
float FUN_00439efc(float param_1,float param_2)

{
  float fVar1;
  
  fVar1 = param_1;
  if ((!NAN(param_2)) &&
     (((param_1 != 0.0 || (fVar1 = param_2, param_2 != 0.0)) && (fVar1 = param_1, param_2 < param_1)
      ))) {
    fVar1 = param_2;
  }
  return fVar1;
}

