
undefined4 spotmgr_profile_apply_42ab7c(void)

{
  int *piVar1;
  
  piVar1 = DAT_0042ac50;
  if (*DAT_0042ac50 == DAT_0042ace4) {
    *DAT_0042ad2c = *DAT_0042ad2c & 0xfffffc00 | (uint)DAT_0042ac50[8] >> 7 & 0x3ff;
    *DAT_0042ad30 = *DAT_0042ad30 & 0xffffffc0 | (uint)piVar1[0x1a] >> 2 & 0x3f;
    *DAT_0042ad34 = *DAT_0042ad34 & 0xfffe7fff | (piVar1[0x1a] & 3U) << 0xf;
  }
  return 0;
}

