
void gx8002_watchdog_ping(void)

{
  uRam0000000c = 0x76;
  return;
}

