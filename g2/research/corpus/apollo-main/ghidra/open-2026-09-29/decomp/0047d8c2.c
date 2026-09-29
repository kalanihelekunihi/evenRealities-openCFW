
uint UX_GetPeerOTAStatus(void)

{
  return (*DAT_0047d900 & 3) >> 1;
}

