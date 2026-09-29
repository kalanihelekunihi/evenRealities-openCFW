
uint FUN_0044d234(int *param_1)

{
  uint uVar1;
  
  do {
    param_1 = (int *)*param_1;
    if (param_1 == (int *)0x0) break;
  } while ((param_1[8] & 0xfffffU) >> 4 == 0);
  if (param_1 == (int *)0x0) {
    uVar1 = 0;
  }
  else {
    uVar1 = (param_1[8] & 0xfffffU) >> 4;
  }
  return uVar1;
}

