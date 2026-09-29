
undefined4 spotmgr_transition_sequence_2b_428378(void)

{
  uint *puVar1;
  undefined4 unaff_r7;
  
  *DAT_00428c84 = *DAT_00428c84 & 0xffffff80 | *DAT_00428c98 & 0x7f;
  puVar1 = DAT_00428ca0;
  *DAT_00428ca0 = *DAT_00428ca0 & 0xffffc3ff | (*DAT_00428c94 & 0xf) << 10;
  *puVar1 = *puVar1 & 0xfffffc00 | *DAT_00428c90 & 0x3ff;
  delay_us(5);
  puVar1 = DAT_00428c9c;
  *DAT_00428c9c = *DAT_00428c9c & 0xfffeffff;
  *puVar1 = *puVar1 & 0xfdffffff;
  *DAT_00428ba8 = *DAT_00428ba8 & 0xffffff80 | *DAT_00428a90 & 0x7f;
  *DAT_00428c88 = 0x1a;
  return unaff_r7;
}

