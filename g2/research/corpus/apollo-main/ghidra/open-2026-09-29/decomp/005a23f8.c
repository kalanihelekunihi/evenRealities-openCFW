
undefined4 FUN_005a23f8(void)

{
  uint *puVar1;
  undefined4 unaff_r7;
  
  *DAT_005a2d04 = *DAT_005a2d04 & 0xffffff80 | *DAT_005a2d18 & 0x7f;
  puVar1 = DAT_005a2d20;
  *DAT_005a2d20 = *DAT_005a2d20 & 0xffffc3ff | (*DAT_005a2d14 & 0xf) << 10;
  *puVar1 = *puVar1 & 0xfffffc00 | *DAT_005a2d10 & 0x3ff;
  FUN_004807a0(5);
  puVar1 = DAT_005a2d1c;
  *DAT_005a2d1c = *DAT_005a2d1c & 0xfffeffff;
  *puVar1 = *puVar1 & 0xfdffffff;
  *DAT_005a2c28 = *DAT_005a2c28 & 0xffffff80 | *DAT_005a2b10 & 0x7f;
  *DAT_005a2d08 = 0x1a;
  return unaff_r7;
}

