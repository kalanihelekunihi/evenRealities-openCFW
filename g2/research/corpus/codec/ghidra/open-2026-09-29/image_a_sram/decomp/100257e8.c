
void gx8002_timer_initialize(void)

{
  uint uVar1;
  
  gx8002_platform_gate(0x17,1);
  uRam00000010 = 0;
  uRam00000020 = 3;
  uVar1 = gx8002_clock_frequency(0x17);
  iRam00000024 = uVar1 / 1000000 - 1;
  uRam00000028 = 0xfffffc18;
  uRam00000010 = 2;
  func_0x102099cc(uRam10025854,0,0x168);
  gx8002_request_irq(0xe,uRam10025858,0);
  gx8002_timer_channel_initialize();
  uRam000000a0 = 1;
  uRam000000a4 = 0;
  uRam000000a8 = 0;
  uRam00000090 = 2;
  return;
}

