
void case_gpio_policy_update(int param_1,int param_2)

{
  uint uVar1;
  
  uVar1 = *(uint *)(DAT_08003f10 + 0x14) & DAT_08003f14;
  if (param_1 == 4) {
    uVar1 = uVar1 & 0xffffdfff;
  }
  else {
    uVar1 = uVar1 | 0x2000;
  }
  *(uint *)(DAT_08003f10 + 0x14) = param_2 << 3 | uVar1 | DAT_08003f18;
  return;
}

