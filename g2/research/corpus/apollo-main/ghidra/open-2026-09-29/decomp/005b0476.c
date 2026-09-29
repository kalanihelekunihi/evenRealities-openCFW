
undefined4 FUN_005b0476(int param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  char cVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  
  uVar6 = param_3;
  FUN_005b01ca();
  iVar2 = DAT_005b0a54;
  pcVar1 = DAT_005b0a50;
  if (param_1 == 0) {
    cVar3 = APP_PbConversateRxFrameDataProcess(param_2,param_3 & 0xffff,DAT_005b0a54);
    *pcVar1 = cVar3;
    if (*pcVar1 == '\r') {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(2,DAT_005b09f4,DAT_005b09f0,DAT_005b0a5c,0xae,DAT_005b0a58,uVar6,param_4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_005b0a60,DAT_005b0a60);
      }
      *pcVar1 = '\0';
      APP_PbConversateTxEncodeCommResp(pcVar1,*(undefined1 *)(iVar2 + 1));
    }
    else if (*pcVar1 == '\0') {
      iVar4 = FUN_005b08a2(iVar2);
      if (iVar4 == 0) {
        *pcVar1 = '\0';
        APP_PbConversateTxEncodeCommResp(pcVar1,*(undefined1 *)(iVar2 + 1));
        FUN_005b03c2();
      }
      else {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(2,DAT_005b09f4,DAT_005b09f0,DAT_005b0a5c,0xbb,DAT_005b0a6c,iVar4,param_4);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_005b0a70,DAT_005b0a70,iVar4);
        }
        *pcVar1 = '\x01';
        APP_PbConversateTxEncodeCommResp(pcVar1,*(undefined1 *)(iVar2 + 1));
      }
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(2,DAT_005b09f4,DAT_005b09f0,DAT_005b0a5c,0xb4,DAT_005b0a64,*pcVar1,param_4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_005b0a68,DAT_005b0a68,*pcVar1);
      }
      *pcVar1 = '\x01';
      APP_PbConversateTxEncodeCommResp(pcVar1,*(undefined1 *)(iVar2 + 1));
    }
  }
  FUN_005b0284();
  return 0;
}

