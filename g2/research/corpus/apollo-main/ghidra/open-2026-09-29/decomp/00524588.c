
uint ft_div64by32(uint param_1,uint param_2,uint param_3)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  if (param_1 < param_3) {
    iVar2 = FT_MSB(param_1);
    uVar3 = 0x1f - iVar2;
    uVar4 = param_1 << (uVar3 & 0xff) | param_2 >> (0x20 - uVar3 & 0xff);
    param_2 = param_2 << (uVar3 & 0xff);
    uVar1 = uVar4 / param_3;
    uVar4 = uVar4 - param_3 * uVar1;
    iVar2 = 0x20 - uVar3;
    do {
      uVar1 = uVar1 << 1;
      uVar4 = param_2 >> 0x1f | uVar4 << 1;
      param_2 = param_2 << 1;
      if (param_3 <= uVar4) {
        uVar4 = uVar4 - param_3;
        uVar1 = uVar1 | 1;
      }
      iVar2 = iVar2 + -1;
    } while (iVar2 != 0);
  }
  else {
    uVar1 = 0x7fffffff;
  }
  return uVar1;
}

