
void gx_rtc_start_tick(void)

{
  *(uint *)(iRam102066ac + 0xc) = *(uint *)(iRam102066ac + 0xc) | 4;
  return;
}

