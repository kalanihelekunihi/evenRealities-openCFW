
undefined4 FUN_0041ccd6(void)

{
  undefined4 unaff_r7;
  
  *DAT_0041d0f0 = *DAT_0041d0f0 & 0xfffffffe;
  *DAT_0041d108 = *DAT_0041d108 & 0xffff7fff;
  clock_release(4,0x31);
  *DAT_0041d114 = 0x40000;
  *DAT_0041d100 = 0xc0000000;
  *DAT_0041d110 = 0x40000;
  return unaff_r7;
}

