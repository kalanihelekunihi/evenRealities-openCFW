
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void wait_bus_ready(void)

{
  do {
  } while ((_DAT_a2000028 & 1) != 0);
  return;
}

