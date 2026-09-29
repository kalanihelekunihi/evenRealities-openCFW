
void gx8002_watchdog_stop(void)

{
  uRam00000000 = uRam00000000 & 0xfffffffe;
  return;
}

