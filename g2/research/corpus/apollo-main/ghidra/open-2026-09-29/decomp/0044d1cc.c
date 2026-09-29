
bool FUN_0044d1cc(undefined4 *param_1)

{
  bool bVar1;
  
  param_1 = (undefined4 *)*param_1;
  while ((param_1 != (undefined4 *)0x0 && ((param_1[8] & 0xf) >> 2 == 0))) {
    param_1 = (undefined4 *)*param_1;
  }
  if (param_1 == (undefined4 *)0x0) {
    bVar1 = false;
  }
  else {
    bVar1 = (param_1[8] & 0xf) >> 2 == 1;
  }
  return bVar1;
}

