
uint FUN_00455820(char *param_1)

{
  uint uVar1;
  
  uVar1 = 0;
  for (; *param_1 == -0x5b; param_1 = param_1 + 1) {
    uVar1 = uVar1 + 1;
  }
  return uVar1 >> 2 & 0xffff;
}

