
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_004e923c(void)

{
  uint unaff_r7;
  
  if ((*DAT_004e939c == 1) && (*DAT_004e93bc < 5)) {
    if (*(char *)(_DAT_004e9cf8 + *DAT_004e93bc) == '\0') {
      FUN_004f2cec();
    }
    else if (*(char *)(_DAT_004e9cf8 + *DAT_004e93bc) == '\x04') {
      FUN_004f8878();
    }
  }
  return (ulonglong)unaff_r7 << 0x20;
}

