
undefined4 APP_PbRxOnboardingFrameDataProcess(int param_1,undefined2 param_2)

{
  byte bVar1;
  byte *pbVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  undefined1 auStack_34 [12];
  int local_28;
  undefined1 auStack_24 [16];
  
  iVar4 = FUN_0043d0ce(0);
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004a8340,DAT_004a84d4,DAT_004a833c,0x30,DAT_004a81b0,param_2);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004a8344,DAT_004a8344,param_2);
  }
  pbVar2 = DAT_004a8350;
  if (param_1 == 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004a8340,DAT_004a84d4,DAT_004a833c,0x32,DAT_004a8348);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004a834c,DAT_004a834c);
    }
    return 2;
  }
  FUN_0043c0e4(DAT_004a8350,0x10,0);
  FUN_0048f49c(auStack_24,param_1,param_2);
  FUN_00439c04(auStack_34,auStack_24,0x10);
  cVar3 = FUN_00490120(auStack_34,DAT_004a8354,pbVar2);
  if (cVar3 == '\0') {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      iVar4 = DAT_004a84d8;
      if (local_28 != 0) {
        iVar4 = local_28;
      }
      FUN_0043d574(1,DAT_004a8340,DAT_004a84d4,DAT_004a833c,0x3c,DAT_004a8358,iVar4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      iVar4 = DAT_004a84d8;
      if (local_28 != 0) {
        iVar4 = local_28;
      }
      compress_log_output(0x4400000,DAT_004a835c,DAT_004a835c,iVar4);
    }
    return 0x2b;
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004a8340,DAT_004a84d4,DAT_004a833c,0x40,DAT_004a8360,*pbVar2);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004a8364,DAT_004a8364,*pbVar2);
  }
  bVar1 = *pbVar2;
  if (bVar1 != 1) {
    if (bVar1 != 0) {
      if (bVar1 == 3) {
        iVar4 = PB_RxOnboardingEvent(pbVar2[1],pbVar2 + 4);
        if (iVar4 != 0) {
          return 1;
        }
        uVar5 = APP_PbTxEncodeOnboardingEvent(pbVar2[1],pbVar2 + 4);
        return uVar5;
      }
      if (bVar1 < 3) {
        iVar4 = PB_RxOnboardingHeartbeat(pbVar2[1],pbVar2 + 4);
        if (iVar4 != 0) {
          return 1;
        }
        uVar5 = APP_PbTxEncodeOnboardingHeartbeat(pbVar2[1],pbVar2 + 4);
        return uVar5;
      }
    }
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004a8340,DAT_004a84d4,DAT_004a833c,0x5d,DAT_004a84dc,*pbVar2);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_004a84e0,DAT_004a84e0,*pbVar2);
    }
    return 1;
  }
  iVar4 = PB_RxOnboardingConfig(pbVar2[1],pbVar2 + 4);
  if (iVar4 != 0) {
    return 1;
  }
  uVar5 = APP_PbTxEncodeOnboardingConfig(pbVar2[1],pbVar2 + 4);
  return uVar5;
}

