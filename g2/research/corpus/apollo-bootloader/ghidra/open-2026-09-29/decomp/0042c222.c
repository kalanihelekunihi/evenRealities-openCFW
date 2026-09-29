
uint rounded_divider_42c222(uint param_1,int param_2,int param_3,int param_4,int param_5)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (param_5 * param_4 + 1) * (param_3 * 2 + 1) * (1 << (param_2 - 1U & 0xff));
  uVar1 = param_1 / uVar2;
  if (uVar2 >> 1 < param_1 - uVar2 * (param_1 / uVar2)) {
    uVar1 = uVar1 + 1;
  }
  return uVar1;
}

