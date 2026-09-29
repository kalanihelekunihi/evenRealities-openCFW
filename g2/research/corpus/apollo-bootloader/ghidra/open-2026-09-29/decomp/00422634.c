
undefined8 FUN_00422634(uint param_1,uint param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (param_2 & 0x7fffffff) >> 0x14;
  if (uVar3 == 0) {
    if (param_1 != 0 || (param_2 & 0x7fffffff) != 0) {
      uVar3 = param_2 & ~(param_2 & 0x80000000);
      iVar1 = LZCOUNT(uVar3);
      if (uVar3 == 0) {
        iVar1 = LZCOUNT(param_1) + 0x20;
      }
      uVar2 = iVar1 - 0xb;
      if (0x1f < uVar2) {
        uVar3 = param_1 << (iVar1 - 0x2bU & 0xff);
      }
      else {
        uVar3 = uVar3 << (uVar2 & 0xff);
      }
      uVar3 = uVar3 | param_2 & 0x80000000;
      if (0x1f >= uVar2) {
        uVar3 = uVar3 | param_1 >> (0x20 - uVar2 & 0xff);
      }
      return CONCAT44(uVar3 + 0x3fd00000,param_1 << (uVar2 & 0xff));
    }
  }
  else if (param_2 << 1 < 0xffe00000) {
    return CONCAT44(param_2 + (uVar3 - 0x3fe) * -0x100000,param_1);
  }
  return CONCAT44(param_2,param_1);
}

