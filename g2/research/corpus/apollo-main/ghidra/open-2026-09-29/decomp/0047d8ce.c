
bool UX_GetSystemBLEStatus(void)

{
  return (*DAT_0047d900 & 0xc) == 0xc;
}

