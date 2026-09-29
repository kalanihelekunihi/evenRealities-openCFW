
undefined4 gx_gpio_set_level(uint param_1,int param_2)

{
  uint uVar1;
  
  uVar1 = 1 << (param_1 & 0x1f);
  if (param_2 == 0) {
    uRama0001004 = uRama0001004 & ~uVar1;
  }
  else {
    uRama0001004 = uVar1 | uRama0001004;
  }
  return 0;
}

