
void CHG_CompareAndUpdateIsCharging(void)

{
  bool bVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  undefined4 in_r3;
  char cVar5;
  undefined1 auStack_20 [8];
  undefined4 uStack_18;
  
  uStack_18 = in_r3;
  FUN_0043c0e4(auStack_20,8,0);
  iVar3 = charger_get_local_battery_info(auStack_20);
  piVar2 = DAT_004ad924;
  if (iVar3 == 0) {
    if (*DAT_004ad924 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004ad910,DAT_004ad90c,DAT_004ad970,0xca,DAT_004ad950);
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
        bVar1 = false;
        cVar5 = '\0';
        if (*(char *)(DAT_004ad908 + 0xc) == '\x01') {
          if (((char)DAT_004ad930[1] == '\x01') || (*DAT_004ad930 == 100)) {
            cVar5 = '\x01';
          }
        }
        else if (((char)DAT_004ad930[1] == '\x01') &&
                ((*(char *)(DAT_004ad908 + 0xc) == '\x01' || (*(int *)(DAT_004ad908 + 8) == 100))))
        {
          cVar5 = '\x01';
        }
        if (cVar5 != *(char *)(DAT_004ad908 + 0x14)) {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(3,DAT_004ad910,DAT_004ad90c,DAT_004ad970,0xe9,DAT_004ad974,
                         (int)*(char *)(iVar3 + 0x14),cVar5);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0xc800000,DAT_004ad978,DAT_004ad978,(int)*(char *)(iVar3 + 0x14),
                                cVar5);
          }
          *(char *)(iVar3 + 0x14) = cVar5;
          bVar1 = true;
        }
        osMutexRelease(*piVar2);
        if (bVar1) {
          CB_CHG_NotifyBatInfo(1,(int)*(char *)(iVar3 + 0x14));
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004ad910,DAT_004ad90c,DAT_004ad970,0xd0,DAT_004ad958);
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
      FUN_0043d574(1,DAT_004ad910,DAT_004ad90c,DAT_004ad970,0xc5,DAT_004ad944);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ad94c,DAT_004ad94c);
    }
  }
  return;
}

