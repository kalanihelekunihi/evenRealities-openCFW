
void CHG_OnBatteryLevelChanged(void)

{
  bool bVar1;
  int *piVar2;
  byte *pbVar3;
  char cVar4;
  int iVar5;
  int local_14;
  char local_10;
  
  cVar4 = FUN_0045a568();
  FUN_0043c0e4(&local_14,8,0);
  charger_get_local_battery_info(&local_14);
  piVar2 = DAT_004ad930;
  bVar1 = false;
  iVar5 = *DAT_004ad930;
  if (iVar5 != local_14) {
    *DAT_004ad930 = local_14;
  }
  pbVar3 = DAT_004ad934;
  if ((char)piVar2[1] == local_10) {
    *DAT_004ad934 = 0;
  }
  else {
    *DAT_004ad934 = *DAT_004ad934 + 1;
    if ((*(int *)(DAT_004ad97c + 4) < 0x62) || (3 < *pbVar3)) {
      *pbVar3 = 0;
      *(char *)(piVar2 + 1) = local_10;
      bVar1 = true;
    }
  }
  if ((iVar5 == local_14 && !bVar1) && (iVar5 = _CHG_HandleInitSync(), iVar5 != 1)) {
    return;
  }
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004ad910,DAT_004ad90c,DAT_004ad984,0x118,DAT_004ad980,cVar4);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004ad988,DAT_004ad988,cVar4);
  }
  if (cVar4 == '\x01') {
    CHG_SendBatteryInfoToPeer(3);
  }
  else {
    CHG_RequestNotifyBatteryInfoFromPeer();
  }
  return;
}

