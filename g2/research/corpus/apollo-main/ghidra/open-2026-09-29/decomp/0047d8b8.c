
byte UX_GetSelfOTAStatus(void)

{
  return *DAT_0047d900 & 1;
}

