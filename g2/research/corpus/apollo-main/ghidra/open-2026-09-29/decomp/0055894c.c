
undefined4 APP_PbRxQuicklistFrameDataProcess(int param_1,undefined2 param_2)

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
    FUN_0043d574(4,DAT_00559194,DAT_0055936c,DAT_00559190,0x2e,DAT_0055918c,param_2);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00559198,DAT_00559198,param_2);
  }
  pbVar2 = DAT_005591a4;
  if (param_1 == 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00559194,DAT_0055936c,DAT_00559190,0x30,DAT_0055919c);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005591a0,DAT_005591a0);
    }
    uVar5 = 2;
  }
  else {
    FUN_0043c0e4(DAT_005591a4,0x1238,0);
    FUN_0048f49c(auStack_24,param_1,param_2);
    FUN_00439c04(auStack_34,auStack_24,0x10);
    cVar3 = FUN_00490120(auStack_34,DAT_005591a8,pbVar2);
    if (cVar3 == '\0') {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        iVar4 = DAT_00559434;
        if (local_28 != 0) {
          iVar4 = local_28;
        }
        FUN_0043d574(1,DAT_00559194,DAT_0055936c,DAT_00559190,0x3a,DAT_005591ac,iVar4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        iVar4 = DAT_00559434;
        if (local_28 != 0) {
          iVar4 = local_28;
        }
        compress_log_output(0x4400000,DAT_00559370,DAT_00559370,iVar4);
      }
      uVar5 = 0x2b;
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00559194,DAT_0055936c,DAT_00559190,0x3e,DAT_00559374,*pbVar2);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_00559438,DAT_00559438,*pbVar2);
      }
      bVar1 = *pbVar2;
      if (bVar1 == 1) {
        iVar4 = PB_RxQuicklistItem(pbVar2[1],pbVar2 + 8);
        if (iVar4 == 0) {
          uVar5 = APP_PbTxEncodeQuicklistItem(pbVar2[1],pbVar2 + 8);
          return uVar5;
        }
      }
      else if (bVar1 != 0) {
        if (bVar1 == 3) {
          iVar4 = PB_RxQuicklistEvent(pbVar2[1],pbVar2 + 8);
          if (iVar4 == 0) {
            uVar5 = APP_PbTxEncodeQuicklistEvent(pbVar2[1],pbVar2 + 8);
            return uVar5;
          }
        }
        else if (bVar1 < 3) {
          iVar4 = PB_RxQuicklistMultItems(pbVar2[1],pbVar2 + 8);
          if (iVar4 == 0) {
            uVar5 = APP_PbTxEncodeQuicklistMultItems(pbVar2[1],pbVar2 + 8);
            return uVar5;
          }
        }
      }
      uVar5 = 1;
    }
  }
  return uVar5;
}

