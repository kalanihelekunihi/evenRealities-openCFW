
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 gx8002_flash_command_read(undefined4 param_1,undefined1 *param_2,int param_3)

{
  undefined1 *puVar1;
  
  wait_bus_ready();
  _DAT_a200004c = 0;
  _DAT_a2000000 = 0xc07;
  _DAT_a2000004 = param_3 + -1;
  _DAT_a2000010 = 1;
  puVar1 = param_2 + param_3;
  _DAT_a2000018 = 0;
  _DAT_a20000f4 = 0;
  _DAT_a2000008 = 1;
  _DAT_a2000060 = param_1;
  for (; param_2 != puVar1; param_2 = param_2 + 1) {
    do {
    } while ((_DAT_a2000028 & 8) == 0);
    *param_2 = (char)_DAT_a2000060;
  }
  gx8002_spi_wait_rx_empty();
  return 0;
}

