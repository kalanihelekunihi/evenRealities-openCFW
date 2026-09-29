
byte FUN_0048d620(void)

{
  byte bVar1;
  
  if (((*DAT_0048d708 == '\0') || ((*DAT_0048d704 & 0xf) == 0)) || ((int)*DAT_0048d704 < 0)) {
    bVar1 = 0;
  }
  else {
    bVar1 = (byte)((*DAT_0048d704 << 1) >> 0x1f) ^ 1;
  }
  return bVar1;
}

