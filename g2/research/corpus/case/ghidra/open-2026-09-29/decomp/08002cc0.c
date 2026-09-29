
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 ota_image_be32_sum_verify(void)

{
  int iVar1;
  byte *pbVar2;
  int iVar3;
  
  iVar1 = DAT_08002d14;
  iVar3 = 0;
  for (pbVar2 = DAT_08002d10; pbVar2 < DAT_08002d10 + *(int *)(DAT_08002d14 + 0x20);
      pbVar2 = pbVar2 + 4) {
    iVar3 = iVar3 + ((uint)pbVar2[3] | (uint)*pbVar2 << 0x18 |
                    (uint)pbVar2[1] << 0x10 | (uint)pbVar2[2] << 8);
  }
  if (*_DAT_08002d18 == '\0') {
    g2_log_printf(s__OTA_BOX___crc_cal__0x_x__crc_rx_08002d1b + 1,iVar3,
                  *(undefined4 *)(DAT_08002d14 + 0x24));
    g2_log_printf(&DAT_08002d44);
  }
  if (*(int *)(iVar1 + 0x24) == iVar3) {
    return 1;
  }
  return 0;
}

