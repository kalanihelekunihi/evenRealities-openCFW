
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 gx8002_flash_uid_read(undefined1 *param_1,int param_2,int *param_3)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  undefined1 *puVar4;
  
  cVar1 = *(char *)(*(int *)(iRam1002418c + 0xc) + 6);
  if ((cVar1 == -0x7b) || (cVar1 == '^')) {
    iVar3 = (uint)(param_2 < 0x10) * param_2 + (uint)(param_2 >= 0x10) * 0x10;
    *param_3 = iVar3;
    wait_bus_ready();
    _DAT_a200004c = 0;
    _DAT_a2000000 = 0xc07;
    _DAT_a2000004 = iVar3 + -1;
    _DAT_a2000010 = 1;
    _DAT_a2000018 = 0x40000;
    puVar4 = param_1 + iVar3;
    _DAT_a20000f4 = 0;
    _DAT_a2000008 = 1;
    _DAT_a2000060 = 0;
    for (; puVar4 != param_1; param_1 = param_1 + 1) {
      do {
      } while ((_DAT_a2000028 & 8) == 0);
      *param_1 = (char)_DAT_a2000060;
    }
    gx8002_spi_wait_rx_empty();
    uVar2 = 0;
  }
  else {
    *param_3 = 0;
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

