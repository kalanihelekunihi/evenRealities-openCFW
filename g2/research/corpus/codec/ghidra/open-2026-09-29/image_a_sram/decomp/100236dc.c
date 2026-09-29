
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 gx8002_flash_command_write(undefined4 param_1,undefined4 *param_2,int param_3)

{
  undefined4 *puVar1;
  
  wait_bus_ready();
  _DAT_a2000018 = param_3 << 0x10;
  _DAT_a200004c = 0;
  _DAT_a2000000 = 0x407;
  _DAT_a2000010 = 1;
  puVar1 = (undefined4 *)(param_3 + (int)param_2);
  _DAT_a20000f4 = 0;
  _DAT_a2000008 = 1;
  _DAT_a2000060 = param_1;
  for (; param_2 != puVar1; param_2 = (undefined4 *)((int)param_2 + 1)) {
    do {
    } while ((_DAT_a2000028 & 2) == 0);
    _DAT_a2000060 = *param_2;
  }
  _DAT_a2000004 = param_3;
  gx8002_spi_wait_tx_empty();
  return 0;
}

