
uint UX_GetPeerRingStatus(void)

{
  return (*DAT_0047d900 & 0x3f) >> 5;
}

