
longlong FUN_0059fbac(char param_1)

{
  uint *puVar1;
  uint uVar2;
  uint unaff_r7;
  
  if (param_1 != '\x02') {
    FUN_004803c2(1,0);
  }
  puVar1 = DAT_0059ffa0;
  if ((*DAT_0059ff9c & 0x3f) >> 4 == 3) {
    if (*DAT_0059ffb0 != '\0') {
      FUN_0059fb70(0);
      *DAT_0059ffa0 = *DAT_0059ffa0 & 0xffffc3ff | 0x400;
      if (*DAT_0059ffb4 + 9U < 0x80) {
        uVar2 = *DAT_0059ffb4 + 9;
      }
      else {
        uVar2 = 0x7f;
      }
      *DAT_0059ffb8 = *DAT_0059ffb8 & 0xffffff80 | uVar2 & 0x7f;
      *DAT_0059ffbc = *DAT_0059ffbc | 0x100;
      if (*DAT_0059ffc0 + 0xfU < 0x80) {
        uVar2 = *DAT_0059ffc0 + 0xf;
      }
      else {
        uVar2 = 0x7f;
      }
      *DAT_0059ffc4 = *DAT_0059ffc4 & 0xffffff80 | uVar2 & 0x7f;
      *DAT_0059ffc8 = *DAT_0059ffc8 | 0x60000000;
      FUN_0059fb70(1);
      FUN_004807a0(0xf);
    }
  }
  else {
    *DAT_0059ffa4 = (*DAT_0059ffa0 & 0x3fff) >> 10;
    *puVar1 = *puVar1 & 0xffffc3ff | 0x800;
    puVar1 = DAT_0059ffa8;
    *DAT_0059ffac = *DAT_0059ffa8 & 0x3f;
    if ((*puVar1 & 0x3f) + 5 < 0x40) {
      uVar2 = (*puVar1 & 0x3f) + 5;
    }
    else {
      uVar2 = 0x3f;
    }
    *puVar1 = *puVar1 & 0xffffffc0 | uVar2 & 0x3f;
    FUN_004807a0(0xf);
  }
  return (ulonglong)unaff_r7 << 0x20;
}

