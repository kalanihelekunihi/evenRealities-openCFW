
undefined4 smpDbStartServiceTimer(void)

{
  undefined4 unaff_r7;
  
  if (*(char *)(DAT_005429f4 + 0xfd) == '\0') {
    WsfTimerStartMs(DAT_005429f4 + 0xf0,1000);
  }
  return unaff_r7;
}

