
uint UX_GetSelfRingStatus(void)

{
  return (*DAT_0047d900 & 0x1f) >> 4;
}

