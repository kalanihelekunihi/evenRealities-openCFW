
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 gx8002_flash_otp_transmit(int param_1,uint *param_2,int param_3)

{
  int iVar1;
  uint *puVar2;
  
  wait_bus_ready();
  uRam00000090 = 2;
  _DAT_a200004c = 0;
  _DAT_a2000000 = 0x407;
  _DAT_a2000004 = param_3 + -1;
  _DAT_a2000018 = 0;
  _DAT_a20000f4 = 0;
  _DAT_a2000050 = 8;
  _DAT_a2000008 = 1;
  for (iVar1 = 0; iVar1 != param_1; iVar1 = iVar1 + 1) {
    do {
    } while ((_DAT_a2000028 & 2) == 0);
    _DAT_a2000060 = (uint)*(byte *)(DAT_10023eb4 + iVar1 + 0x10);
  }
  _DAT_a2000010 = 1;
  puVar2 = (uint *)(param_3 + (int)param_2);
  for (; param_2 != puVar2; param_2 = (uint *)((int)param_2 + 1)) {
    do {
    } while ((_DAT_a2000028 & 2) == 0);
    _DAT_a2000060 = *param_2;
  }
  gx8002_spi_wait_tx_empty();
  uRam00000090 = 1;
  _DAT_a2000008 = 1;
  gx8002_flash_wait_ready();
  return 0;
}

