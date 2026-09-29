
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 gx8002_flash_word_read(undefined4 param_1,int param_2,uint param_3)

{
  uint uVar1;
  
  if (param_3 != 0) {
    wait_bus_ready();
    _DAT_a2000000 = 0x81f;
    _DAT_a2000004 = (param_3 >> 2) - 1;
    _DAT_a2000018 = 0;
    _DAT_a2000054 = 7;
    _DAT_a200004c = 1;
    if ((uint)(*(int *)(*(int *)(DAT_10023d50 + 0xc) + 4) + DAT_10023d54) < 2) {
      _DAT_a20000f4 = 0x40003219;
    }
    else {
      _DAT_a20000f4 = 0x40004218;
    }
    _DAT_a2000008 = 1;
    _DAT_a2000010 = 1;
    _DAT_a2000064 = param_1;
    for (uVar1 = 0; param_3 >> 2 != uVar1; uVar1 = uVar1 + 1) {
      do {
      } while ((_DAT_a2000028 & 8) == 0);
      *(undefined4 *)(param_2 + uVar1 * 4) = _DAT_a2000060;
    }
    gx8002_spi_wait_rx_empty();
    _DAT_a200004c = 0;
    _DAT_a2000008 = 1;
  }
  return 0;
}

