
void CHG_ReceiveBatteryInfoFromPeer(char *param_1)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  
  if (param_1 == (char *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004ad910,DAT_004ad90c,DAT_004ad99c,0x146,DAT_004ad998);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ad9a0,DAT_004ad9a0);
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004ad910,DAT_004ad90c,DAT_004ad99c,0x14b,DAT_004ad9a4,*param_1,
                   *(undefined4 *)(param_1 + 4),(int)param_1[8]);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10c00000,DAT_004ad9a8,DAT_004ad9a8,*param_1,*(undefined4 *)(param_1 + 4)
                          ,(int)param_1[8]);
    }
    FUN_0045a568();
    piVar1 = DAT_004ad924;
    if (*DAT_004ad924 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004ad910,DAT_004ad90c,DAT_004ad99c,0x151,DAT_004ad950);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004ad954,DAT_004ad954);
      }
    }
    else {
      iVar3 = osMutexAcquire(*DAT_004ad924,0xffffffff);
      iVar2 = DAT_004ad908;
      if (iVar3 == 0) {
        *(undefined4 *)(DAT_004ad908 + 8) = *(undefined4 *)(param_1 + 4);
        *(char *)(iVar2 + 0xc) = param_1[8];
        osMutexRelease(*piVar1);
        if (*param_1 == '\x03') {
          CHG_SendBatteryInfoToPeer(2);
          CHG_CompareAndUpdateSoc();
          CHG_CompareAndUpdateIsCharging();
        }
        else if (*param_1 == '\x02') {
          CHG_CompareAndUpdateSoc();
          CHG_CompareAndUpdateIsCharging();
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004ad910,DAT_004ad90c,DAT_004ad99c,0x157,DAT_004ad958);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004ad95c,DAT_004ad95c);
        }
      }
    }
  }
  return;
}

