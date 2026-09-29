
void FUN_005a0b9c(void)

{
  if (*DAT_005a13dc == '\0') {
    *DAT_005a13e0 = *DAT_005a13e0 & 0xffffff80 | *DAT_005a13e4 & 0x7f;
    *DAT_005a16f0 = *DAT_005a16f0 & 0xffffff80 | *DAT_005a16f4 & 0x7f;
  }
  return;
}

