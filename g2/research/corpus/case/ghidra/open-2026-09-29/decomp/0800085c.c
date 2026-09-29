
void gls_rx_buffer_parse_dispatch(void)

{
  ushort uVar1;
  ushort *puVar2;
  char cVar3;
  byte bVar4;
  int iVar5;
  char *pcVar6;
  uint uVar7;
  undefined4 uVar8;
  undefined4 in_r3;
  uint uVar9;
  
  puVar2 = DAT_0800091c;
  uVar1 = *DAT_0800091c;
  if (uVar1 < 2) {
    return;
  }
  if (*(byte *)(DAT_08000920 + 0x17) < 0x1e) {
    *(undefined1 *)(DAT_08000920 + 0x17) = 0;
  }
  pcVar6 = DAT_08000924;
  if (*DAT_08000924 != -0x22) {
    iVar5 = case_hex_value(*DAT_08000924);
    if ((iVar5 != 0xd) || (iVar5 = case_hex_value(pcVar6[1]), iVar5 != 0xe)) {
      uVar7 = (uint)*puVar2;
      if (uVar7 < 5) {
        return;
      }
      if (*pcVar6 != 'Z') {
        return;
      }
      if (pcVar6[1] != -0x5b) {
        return;
      }
      if (pcVar6[2] == '\x7f') {
        uVar9 = (uint)(byte)pcVar6[3];
        if (uVar9 != uVar7 - 5) {
          return;
        }
        uVar7 = uVar7 - 4;
        uVar8 = 0;
        pcVar6 = pcVar6 + 4;
      }
      else {
        if (pcVar6[2] != -0x31) {
          return;
        }
        if ((uint)(byte)pcVar6[3] != (uVar7 - 6 & 0xff)) {
          return;
        }
        uVar9 = (uint)(byte)pcVar6[4];
        if (uVar9 != (int)(uVar7 - 6) >> 8) {
          return;
        }
        uVar7 = uVar7 - 5;
        uVar8 = 1;
        pcVar6 = pcVar6 + 5;
      }
      FUN_08000e1c(pcVar6,uVar7 & 0xffff,uVar8,uVar9,in_r3);
      return;
    }
    for (uVar7 = 1; uVar7 < *puVar2 >> 1; uVar7 = uVar7 + 1 & 0xffff) {
      iVar5 = uVar7 * 2;
      cVar3 = case_hex_value(pcVar6[iVar5]);
      bVar4 = case_hex_value(pcVar6[iVar5 + 1]);
      pcVar6[uVar7] = cVar3 << 4 | bVar4;
    }
    uVar1 = *puVar2 >> 1;
  }
  FUN_08000928(pcVar6 + 1,uVar1 - 1);
  return;
}

