
longlong FUN_0059fca2(void)

{
  uint unaff_r7;
  
  if ((*DAT_0059ff9c & 0x3f) >> 4 == 3) {
    if (*DAT_0059ffb0 != '\0') {
      FUN_0059fb70(0);
      *DAT_0059ffc8 = *DAT_0059ffc8 & 0x9fffffff | (*DAT_0059ffcc & 3) << 0x1d;
      *DAT_0059ffc4 = *DAT_0059ffc4 & 0xffffff80 | *DAT_0059ffc0 & 0x7f;
      *DAT_0059ffbc = *DAT_0059ffbc & 0xfffffeff;
      *DAT_0059ffb8 = *DAT_0059ffb8 & 0xffffff80 | *DAT_0059ffb4 & 0x7f;
      *DAT_0059ffa0 = *DAT_0059ffa0 & 0xffffc3ff | (*DAT_0059ffd0 & 0xf) << 10;
      FUN_0059fb70(1);
    }
  }
  else {
    *DAT_0059ffa8 = *DAT_0059ffa8 & 0xffffffc0 | *DAT_0059ffac & 0x3f;
    *DAT_0059ffa0 = *DAT_0059ffa0 & 0xffffc3ff | (*DAT_0059ffa4 & 0xf) << 10;
  }
  FUN_004803c2(0,0);
  return (ulonglong)unaff_r7 << 0x20;
}

