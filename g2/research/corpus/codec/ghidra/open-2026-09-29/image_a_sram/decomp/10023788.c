
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void gx8002_flash_word_program(undefined4 param_1,int param_2,uint param_3)

{
  uint uVar1;
  
  wait_bus_ready();
  _DAT_a2000000 = 0x41f;
  _DAT_a2000004 = (param_3 >> 2) - 1;
  _DAT_a2000010 = 1;
  _DAT_a2000018 = 0x20000;
  _DAT_a20000f4 = 0x218;
  _DAT_a2000050 = 8;
  _DAT_a200004c = 2;
  _DAT_a2000008 = 1;
  for (uVar1 = 0; uVar1 != param_3 >> 2; uVar1 = uVar1 + 1) {
    do {
    } while ((_DAT_a2000028 & 2) == 0);
    _DAT_a2000060 = *(undefined4 *)(param_2 + uVar1 * 4);
  }
  _DAT_a2000064 = param_1;
  gx8002_spi_wait_tx_empty();
  gx8002_flash_wait_ready();
  _DAT_a200004c = 0;
  _DAT_a2000008 = 1;
  return;
}

