
undefined4 FUN_004802ce(void)

{
  undefined4 unaff_r7;
  
  *DAT_004806d0 = *DAT_004806d0 & 0xfffffffe;
  *DAT_004806e8 = *DAT_004806e8 & 0xffff7fff;
  FUN_004c4530(4,0x31);
  *DAT_004806f4 = 0x40000;
  *DAT_004806e0 = 0xc0000000;
  *DAT_004806f0 = 0x40000;
  return unaff_r7;
}

