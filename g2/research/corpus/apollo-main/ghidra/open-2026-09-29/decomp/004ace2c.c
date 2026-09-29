
undefined4 _CHG_HandleInitSync(void)

{
  char *pcVar1;
  ushort *puVar2;
  byte *pbVar3;
  ushort *puVar4;
  undefined4 uVar5;
  int iVar6;
  undefined4 in_r3;
  
  pcVar1 = DAT_004ad7c8;
  if (*DAT_004ad7c8 == '\0') {
    uVar5 = 0;
  }
  else {
    iVar6 = charger_aggregate_soc_is_valid();
    puVar2 = DAT_004ad7d8;
    if (iVar6 == 0) {
      if (*DAT_004ad7d8 != 0xffff) {
        *DAT_004ad7d8 = *DAT_004ad7d8 + 1;
      }
      puVar4 = DAT_004ad878;
      pbVar3 = DAT_004ad874;
      if (*puVar2 < 0x10) {
        if (*DAT_004ad874 < 4) {
          if (*puVar2 < *DAT_004ad878) {
            uVar5 = 0;
          }
          else {
            *DAT_004ad874 = *DAT_004ad874 + 1;
            *puVar4 = *puVar2 + 2;
            iVar6 = FUN_0043d0ce();
            if (iVar6 << 0x1e < 0) {
              FUN_0043d574(3,DAT_004ad910,DAT_004ad90c,DAT_004ad7d0,0x5d,DAT_004ad87c,*pbVar3,4,2,
                           in_r3);
            }
            iVar6 = FUN_0043d0ce();
            if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
              compress_log_output(0xcc00000,DAT_004ad914,DAT_004ad914,*pbVar3,4,2);
            }
            uVar5 = 1;
          }
        }
        else {
          uVar5 = 0;
        }
      }
      else {
        *pcVar1 = '\0';
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(2,DAT_004ad910,DAT_004ad90c,DAT_004ad7d0,0x4f,DAT_004ad86c);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_004ad870);
        }
        uVar5 = 0;
      }
    }
    else {
      *pcVar1 = '\0';
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(3,DAT_004ad910,DAT_004ad90c,DAT_004ad7d0,0x44,DAT_004ad7cc);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004ad7d4,DAT_004ad7d4);
      }
      uVar5 = 0;
    }
  }
  return uVar5;
}

