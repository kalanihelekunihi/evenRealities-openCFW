
void ft_multo64(uint param_1,uint param_2,uint *param_3)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (param_1 >> 0x10) * (param_2 & 0xffff);
  uVar2 = uVar3 + (param_2 >> 0x10) * (param_1 & 0xffff);
  uVar3 = (param_2 >> 0x10) * (param_1 >> 0x10) + (uint)(uVar2 < uVar3) * 0x10000 + (uVar2 >> 0x10);
  uVar1 = uVar2 * 0x10000 + (param_2 & 0xffff) * (param_1 & 0xffff);
  if (uVar1 < uVar2 * 0x10000) {
    uVar3 = uVar3 + 1;
  }
  *param_3 = uVar1;
  param_3[1] = uVar3;
  return;
}

