
void gx_rtc_start_tick(void)

{
  *(uint *)(iRam1000880c + 0xc) = *(uint *)(iRam1000880c + 0xc) | 4;
  return;
}

