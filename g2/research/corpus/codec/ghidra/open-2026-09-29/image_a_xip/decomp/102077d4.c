
undefined4 gx8002_power_unlock(int param_1)

{
  uint uVar1;
  undefined4 uVar2;
  
  if (param_1 < 0x21) {
    uVar1 = param_1 - 1U & 0x3f;
    *DAT_102077f4 = (-2 << uVar1 | 0xfffffffeU >> 0x20 - uVar1) & *DAT_102077f4;
    uVar2 = 0;
  }
  else {
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

