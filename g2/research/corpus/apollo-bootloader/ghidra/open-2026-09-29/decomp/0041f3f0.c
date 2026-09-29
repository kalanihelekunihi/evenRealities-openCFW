
byte FUN_0041f3f0(void)

{
  byte bVar1;
  
  if (((*DAT_0041f4d8 == '\0') || ((*DAT_0041f4d4 & 0xf) == 0)) || ((int)*DAT_0041f4d4 < 0)) {
    bVar1 = 0;
  }
  else {
    bVar1 = (byte)((*DAT_0041f4d4 << 1) >> 0x1f) ^ 1;
  }
  return bVar1;
}

