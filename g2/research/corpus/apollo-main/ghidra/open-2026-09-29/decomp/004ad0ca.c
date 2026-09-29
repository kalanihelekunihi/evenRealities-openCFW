
void CHG_CompareAndUpdateSoc(void)

{
  char *pcVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined1 auStack_18 [8];
  
  FUN_0043c0e4(auStack_18,8,0);
  iVar3 = charger_get_local_battery_info(auStack_18);
  piVar2 = DAT_004ad924;
  if (iVar3 == 0) {
    if (*DAT_004ad924 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004ad910,DAT_004ad90c,DAT_004ad948,0x99,DAT_004ad950);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004ad954,DAT_004ad954);
      }
    }
    else {
      iVar4 = osMutexAcquire(*DAT_004ad924,0xffffffff);
      iVar3 = DAT_004ad908;
      if (iVar4 == 0) {
        if (*DAT_004ad930 < *(int *)(DAT_004ad908 + 8)) {
          iVar4 = *DAT_004ad930;
        }
        else {
          iVar4 = *(int *)(DAT_004ad908 + 8);
        }
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004ad910,DAT_004ad90c,DAT_004ad948,0xac,DAT_004ad960,
                       *(undefined4 *)(iVar3 + 0x10),iVar4);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0xc800000,DAT_004ad964,DAT_004ad964,*(undefined4 *)(iVar3 + 0x10),
                              iVar4);
        }
        *(int *)(iVar3 + 0x10) = iVar4;
        osMutexRelease(*piVar2);
        pcVar1 = DAT_004ad7c8;
        if ((*DAT_004ad7c8 != '\0') && (iVar4 = charger_aggregate_soc_is_valid(), iVar4 != 0)) {
          *pcVar1 = '\0';
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(3,DAT_004ad910,DAT_004ad90c,DAT_004ad948,0xb7,DAT_004ad968);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0xc000000,DAT_004ad96c,DAT_004ad96c);
          }
        }
        CB_CHG_NotifyBatInfo(0,*(undefined4 *)(iVar3 + 0x10));
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004ad910,DAT_004ad90c,DAT_004ad948,0x9f,DAT_004ad958);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004ad95c,DAT_004ad95c);
        }
      }
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004ad910,DAT_004ad90c,DAT_004ad948,0x94,DAT_004ad944);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ad94c,DAT_004ad94c);
    }
  }
  return;
}

