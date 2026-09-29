
longlong hw_register_profile_restore_42f2fa(void)

{
  uint unaff_r7;
  
  if ((*DAT_0042f5f4 & 0x3f) >> 4 == 3) {
    if (*DAT_0042f608 != '\0') {
      register_power_toggle_42f1c8(0);
      *DAT_0042f620 = *DAT_0042f620 & 0x9fffffff | (*DAT_0042f624 & 3) << 0x1d;
      *DAT_0042f61c = *DAT_0042f61c & 0xffffff80 | *DAT_0042f618 & 0x7f;
      *DAT_0042f614 = *DAT_0042f614 & 0xfffffeff;
      *DAT_0042f610 = *DAT_0042f610 & 0xffffff80 | *DAT_0042f60c & 0x7f;
      *DAT_0042f5f8 = *DAT_0042f5f8 & 0xffffc3ff | (*DAT_0042f628 & 0xf) << 10;
      register_power_toggle_42f1c8(1);
    }
  }
  else {
    *DAT_0042f600 = *DAT_0042f600 & 0xffffffc0 | *DAT_0042f604 & 0x3f;
    *DAT_0042f5f8 = *DAT_0042f5f8 & 0xffffc3ff | (*DAT_0042f5fc & 0xf) << 10;
  }
  FUN_0041cde0(0,0);
  return (ulonglong)unaff_r7 << 0x20;
}

