
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 gx8002_spi_wait_rx_empty(void)

{
  do {
  } while (_DAT_a2000024 != 0);
  wait_bus_ready();
  return 0;
}

