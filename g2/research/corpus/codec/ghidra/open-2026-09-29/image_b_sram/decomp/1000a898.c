
undefined4 FUN_1000a898(int param_1)

{
  uint uVar1;
  
  uVar1 = 1 << (param_1 - 1U & 0x3f);
  if (((DAT_1000a8c0[1] & uVar1) != 0) && (param_1 < 0x21)) {
    *DAT_1000a8c0 = uVar1 | *DAT_1000a8c0;
    return 0;
  }
  return 0xffffffff;
}

