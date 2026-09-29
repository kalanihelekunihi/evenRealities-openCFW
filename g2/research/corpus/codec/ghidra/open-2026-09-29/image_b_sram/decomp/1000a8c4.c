
undefined4 FUN_1000a8c4(int param_1)

{
  uint uVar1;
  
  if (0x20 < param_1) {
    return 0xffffffff;
  }
  uVar1 = param_1 - 1U & 0x3f;
  *DAT_1000a8e8 = (-2 << uVar1 | 0xfffffffeU >> 0x20 - uVar1) & *DAT_1000a8e8;
  return 0;
}

