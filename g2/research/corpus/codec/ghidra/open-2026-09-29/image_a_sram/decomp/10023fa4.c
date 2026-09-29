
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int gx8002_flash_otp_read(int param_1,undefined1 *param_2,int param_3)

{
  short sVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  int iVar5;
  uint uVar6;
  undefined1 *puVar7;
  int iVar8;
  int iVar9;
  int unaff_r8;
  
  iVar2 = DAT_100240f8;
  piVar4 = *(int **)(*(int *)(DAT_100240f8 + 0xc) + 0x14);
  if ((param_3 != 0) && ((uint)(param_3 + param_1) <= (uint)piVar4[2])) {
    iVar9 = *piVar4 + param_1 + (piVar4[4] & 7U) * piVar4[1];
    sVar1 = *(short *)(*(int *)(DAT_100240f8 + 0xc) + 6);
    if ((sVar1 == 0x5e) || (sVar1 == 0x85)) {
      gx8002_flash_wait_ready();
      iVar3 = DAT_100240fc + -8;
      iVar8 = 0;
      *(undefined1 *)(iVar2 + 0x10) = 0x48;
      sflash_addr2cmd_isra_0(iVar3,iVar9);
      iVar3 = DAT_100240fc;
      do {
        unaff_r8 = (uint)(param_3 < 0x20) * unaff_r8 + (uint)(param_3 >= 0x20) * 0x20;
        if (unaff_r8 != 0) {
          iVar5 = *(int *)(iVar2 + 8);
          wait_bus_ready();
          uRam00000090 = 2;
          _DAT_a200004c = 0;
          _DAT_a2000000 = 0x407;
          _DAT_a2000018 = 0;
          _DAT_a20000f4 = 0;
          _DAT_a2000008 = 1;
          for (uVar6 = 0; uVar6 < iVar5 + 2U; uVar6 = uVar6 + 1) {
            do {
            } while ((_DAT_a2000028 & 2) == 0);
            _DAT_a2000060 = (uint)*(byte *)(iVar2 + uVar6 + 0x10);
          }
          _DAT_a2000010 = 1;
          _DAT_a2000004 = iVar5 + 1;
          gx8002_spi_wait_tx_empty();
          _DAT_a2000004 = unaff_r8 + -1;
          _DAT_a2000000 = 0x807;
          _DAT_a2000018 = 0;
          _DAT_a2000054 = 7;
          _DAT_a200004c = 1;
          _DAT_a2000008 = 1;
          _DAT_a2000010 = 1;
          _DAT_a2000060 = 0;
          for (puVar7 = param_2; param_2 + unaff_r8 != puVar7; puVar7 = puVar7 + 1) {
            do {
            } while ((_DAT_a2000028 & 8) == 0);
            *puVar7 = (char)_DAT_a2000060;
          }
          gx8002_spi_wait_rx_empty();
          _DAT_a200004c = 0;
          uRam00000090 = 1;
          _DAT_a2000008 = 1;
        }
        iVar9 = iVar9 + unaff_r8;
        param_3 = param_3 - unaff_r8;
        param_2 = param_2 + unaff_r8;
        iVar8 = iVar8 + unaff_r8;
        sflash_addr2cmd_isra_0(DAT_10024100,iVar9,iVar3);
      } while (param_3 != 0);
      gx8002_flash_wait_ready();
      return iVar8;
    }
  }
  return -1;
}

