
uint FUN_00577d50(uint param_1)

{
  uint uVar1;
  uint uVar2;
  bool bVar3;
  
  uVar1 = (param_1 & 0x7fffffff) >> 0x17;
  uVar2 = uVar1 - 0x7e;
  if (uVar2 == 0 || uVar1 < 0x7e) {
    bVar3 = CARRY4(param_1,param_1);
    if ((param_1 & 0x7fffffff) != 0) {
      param_1 = 0x3f800000;
    }
    if (bVar3) {
      param_1 = 0x80000000;
    }
  }
  else if ((int)uVar2 < 0x18) {
    uVar1 = 0xffffff >> (uVar2 & 0xff);
    if (-1 < (int)param_1) {
      param_1 = param_1 + uVar1;
    }
    return param_1 & ~uVar1;
  }
  return param_1;
}

