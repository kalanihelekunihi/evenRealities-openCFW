
uint round_bits_427da8(uint param_1)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = (param_1 & 0x7fffffff) >> 0x17;
  uVar2 = uVar1 - 0x7e;
  if (uVar2 == 0 || uVar1 < 0x7e) {
    param_1 = param_1 & 0x80000000;
    if (uVar2 == 0) {
      param_1 = param_1 | 0x3f800000;
    }
  }
  else if ((int)uVar2 < 0x18) {
    uVar1 = 0xffffff >> (uVar2 & 0xff);
    return (param_1 & ~(uVar1 >> 1)) + uVar1 & ~uVar1;
  }
  return param_1;
}

