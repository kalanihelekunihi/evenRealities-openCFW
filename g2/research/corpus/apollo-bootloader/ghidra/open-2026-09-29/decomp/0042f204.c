
longlong event_value_profile_42f204(char param_1)

{
  uint *puVar1;
  uint uVar2;
  uint unaff_r7;
  
  if (param_1 != '\x02') {
    FUN_0041cde0(1,0);
  }
  puVar1 = DAT_0042f5f8;
  if ((*DAT_0042f5f4 & 0x3f) >> 4 == 3) {
    if (*DAT_0042f608 != '\0') {
      register_power_toggle_42f1c8(0);
      *DAT_0042f5f8 = *DAT_0042f5f8 & 0xffffc3ff | 0x400;
      if (*DAT_0042f60c + 9U < 0x80) {
        uVar2 = *DAT_0042f60c + 9;
      }
      else {
        uVar2 = 0x7f;
      }
      *DAT_0042f610 = *DAT_0042f610 & 0xffffff80 | uVar2 & 0x7f;
      *DAT_0042f614 = *DAT_0042f614 | 0x100;
      if (*DAT_0042f618 + 0xfU < 0x80) {
        uVar2 = *DAT_0042f618 + 0xf;
      }
      else {
        uVar2 = 0x7f;
      }
      *DAT_0042f61c = *DAT_0042f61c & 0xffffff80 | uVar2 & 0x7f;
      *DAT_0042f620 = *DAT_0042f620 | 0x60000000;
      register_power_toggle_42f1c8(1);
      delay_us(0xf);
    }
  }
  else {
    *DAT_0042f5fc = (*DAT_0042f5f8 & 0x3fff) >> 10;
    *puVar1 = *puVar1 & 0xffffc3ff | 0x800;
    puVar1 = DAT_0042f600;
    *DAT_0042f604 = *DAT_0042f600 & 0x3f;
    if ((*puVar1 & 0x3f) + 5 < 0x40) {
      uVar2 = (*puVar1 & 0x3f) + 5;
    }
    else {
      uVar2 = 0x3f;
    }
    *puVar1 = *puVar1 & 0xffffffc0 | uVar2 & 0x3f;
    delay_us(0xf);
  }
  return (ulonglong)unaff_r7 << 0x20;
}

