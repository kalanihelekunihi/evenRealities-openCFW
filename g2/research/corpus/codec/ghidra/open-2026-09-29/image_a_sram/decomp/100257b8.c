
void gx8002_timer_channel_initialize(void)

{
  uint uVar1;
  
  uRam00000050 = 0;
  uRam00000060 = 1;
  uVar1 = gx8002_clock_frequency(0x17);
  iRam00000064 = uVar1 / 1000000 - 1;
  uRam00000068 = 0;
  uRam00000050 = 2;
  return;
}

