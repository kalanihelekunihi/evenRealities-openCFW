
uint gx8002_trim_state(void)

{
  gx8002_trim_clock_enable();
  return uRam00000030 & 1;
}

