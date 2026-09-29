
longlong FUN_0058f980(uint param_1,uint param_2)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = param_2 >> 0x14 & 0x7ff;
  uVar2 = uVar1 - 0x3fe;
  if (uVar2 == 0 || uVar1 < 0x3fe) {
    param_2 = param_2 & 0x80000000;
    if (uVar2 == 0) {
      param_2 = param_2 | 0x3ff00000;
    }
    param_1 = 0;
  }
  else if ((int)uVar2 < 0x35) {
    if (0x14 < (int)uVar2) {
      uVar1 = 0xffffffff >> (uVar1 - 0x413 & 0xff);
      param_1 = param_1 & ~(uVar1 >> 1);
      return CONCAT44(param_2 + CARRY4(param_1,uVar1),param_1 + uVar1 & ~uVar1);
    }
    uVar1 = 0x1fffff >> (uVar2 & 0xff);
    return (ulonglong)((param_2 & ~(uVar1 >> 1)) + uVar1 & ~uVar1) << 0x20;
  }
  return CONCAT44(param_2,param_1);
}

