
uint FUN_0059f520(uint param_1)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = (param_1 & 0x7fffffff) >> 0x17;
  uVar2 = uVar1 - 0x7e;
  if (uVar2 == 0 || uVar1 < 0x7e) {
    param_1 = param_1 & 0x80000000;
  }
  else if ((int)uVar2 < 0x18) {
    return param_1 & ~(0xffffffU >> (uVar2 & 0xff));
  }
  return param_1;
}

