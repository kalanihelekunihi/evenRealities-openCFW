
longlong FUN_004e80e8(void)

{
  byte bVar1;
  uint unaff_r7;
  
  if (*DAT_004e835c < 5) {
    bVar1 = *(byte *)(DAT_004e8bc4 + *DAT_004e835c);
    if (bVar1 == 0) {
      FUN_004f4030();
    }
    else if (bVar1 == 2) {
      FUN_004eeadc();
    }
    else if (bVar1 < 2) {
      FUN_004eb33c();
    }
    else if (bVar1 == 4) {
      FUN_004f6880();
    }
    else if (bVar1 < 4) {
      FUN_004fc1dc();
    }
  }
  return (ulonglong)unaff_r7 << 0x20;
}

