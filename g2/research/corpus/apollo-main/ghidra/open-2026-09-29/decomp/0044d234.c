
uint FUN_0044d234(undefined4 *param_1)

{
  uint uVar1;
  
  while ((param_1 != (undefined4 *)0x0 && ((param_1[8] & 0xfffff) >> 4 == 0))) {
    param_1 = (undefined4 *)*param_1;
  }
  if (param_1 == (undefined4 *)0x0) {
    uVar1 = 0;
  }
  else {
    uVar1 = (param_1[8] & 0xfffff) >> 4;
  }
  return uVar1;
}

