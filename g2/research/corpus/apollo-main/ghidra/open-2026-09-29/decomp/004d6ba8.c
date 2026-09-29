
undefined4
APP_PbRxNotificationFrameDataProcess
          (int param_1,ushort param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  undefined4 local_88;
  undefined4 local_84;
  uint local_80;
  undefined1 auStack_7c [12];
  uint local_70;
  byte local_6c;
  undefined1 local_6b;
  undefined1 auStack_68 [72];
  undefined1 auStack_20 [16];
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  iVar2 = FUN_0043d0ce(0);
  if (iVar2 << 0x1e < 0) {
    local_80 = (uint)param_2;
    local_84 = DAT_004d7618;
    local_88 = 0x2c;
    FUN_0043d574(4,DAT_004d7694,DAT_004d7690,DAT_004d761c);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004d7620,DAT_004d7620,param_2);
  }
  if (param_1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_84 = DAT_004d7698;
      local_88 = 0x2e;
      FUN_0043d574(1,DAT_004d7694,DAT_004d7690,DAT_004d761c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004d769c,DAT_004d769c);
    }
    uVar3 = 2;
  }
  else {
    FUN_0048949c(&local_6c,0x4c);
    FUN_0048f49c(auStack_20,param_1,param_2);
    FUN_00439c04(auStack_7c,auStack_20,0x10);
    cVar1 = FUN_00490120(auStack_7c,DAT_004d76a0,&local_6c);
    if (cVar1 == '\0') {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_80 = DAT_004d76a4;
        if (local_70 != 0) {
          local_80 = local_70;
        }
        local_84 = DAT_004d76a8;
        local_88 = 0x37;
        FUN_0043d574(1,DAT_004d7694,DAT_004d7690,DAT_004d761c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        uVar4 = DAT_004d76a4;
        if (local_70 != 0) {
          uVar4 = local_70;
        }
        compress_log_output(0x4400000,DAT_004d76ac,DAT_004d76ac,uVar4);
      }
      uVar3 = 0x2b;
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_80 = (uint)local_6c;
        local_84 = DAT_004d76b0;
        local_88 = 0x3b;
        FUN_0043d574(4,DAT_004d7694,DAT_004d7690,DAT_004d761c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004d76b4,DAT_004d76b4,local_6c);
      }
      if (local_6c == 1) {
        iVar2 = PB_RxNotifCtrl(local_6b,auStack_68);
        if (iVar2 == 0) {
          uVar3 = APP_PbTxEncodeNotifCtrl(local_6b,auStack_68);
          return uVar3;
        }
      }
      else if (local_6c == 3) {
        iVar2 = PB_RxNotifWhitelistCtrl(local_6b,auStack_68);
        if (iVar2 == 0) {
          uVar3 = APP_PbTxEncodeNotifWhitelistCtrl(local_6b,auStack_68);
          return uVar3;
        }
      }
      else if (local_6c == 4) {
        iVar2 = PB_RxNotifWhitelistChk(local_6b,auStack_68);
        if (iVar2 == 0) {
          uVar3 = APP_PbTxEncodeNotifWhitelistChk(local_6b,auStack_68);
          return uVar3;
        }
      }
      else {
        local_88 = CONCAT22(local_88._2_2_,*DAT_004d78e8);
        local_88 = CONCAT31(local_88._1_3_,local_6c);
        APP_PbTxEncodeNotifCommResp(local_6b,&local_88);
      }
      uVar3 = 0;
    }
  }
  return uVar3;
}

