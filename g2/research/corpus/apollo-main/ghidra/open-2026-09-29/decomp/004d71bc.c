
undefined4
APP_PbTxEncodeNotifAppIDNotInWhitelist
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  char cVar2;
  short sVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  undefined1 auStack_44 [12];
  uint local_38;
  int local_34;
  undefined1 auStack_30 [20];
  undefined4 uStack_1c;
  
  uStack_1c = param_4;
  iVar4 = file_heap_allocate(0x9c);
  if (iVar4 == 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004d7694,DAT_004d7690,DAT_004d7924,200,DAT_004d7920);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004d7928);
    }
    uVar5 = 2;
  }
  else {
    FUN_0043c0e4(iVar4,0x9c,0);
    FUN_004905f4(auStack_30,iVar4,0x4e);
    FUN_00439c04(auStack_44,auStack_30,0x14);
    *(undefined1 *)(iVar4 + 0x4e) = 2;
    uVar1 = osKernelGetTickCount();
    *(undefined1 *)(iVar4 + 0x4f) = uVar1;
    *(undefined2 *)(iVar4 + 0x50) = 4;
    iVar6 = FUN_0044a43c(param_1);
    FUN_00439be4(iVar4 + 0x54,param_1,iVar6 + 1);
    sVar3 = FUN_0044a43c(param_1);
    *(short *)(iVar4 + 0x52) = sVar3 + 1;
    iVar6 = FUN_0044a43c(param_2);
    FUN_00439be4(iVar4 + 0x76,param_2,iVar6 + 1);
    sVar3 = FUN_0044a43c(param_2);
    *(short *)(iVar4 + 0x74) = sVar3 + 1;
    *(undefined1 *)(iVar4 + 0x96) = 0;
    cVar2 = FUN_00490c32(auStack_44,DAT_004d792c,(undefined1 *)(iVar4 + 0x4e));
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004d7694,DAT_004d7690,DAT_004d7924,0xdf,DAT_004d7930,local_38);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004d7934,DAT_004d7934,local_38);
    }
    if (cVar2 == '\0') {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        iVar6 = DAT_004d76a4;
        if (local_34 != 0) {
          iVar6 = local_34;
        }
        FUN_0043d574(1,DAT_004d7694,DAT_004d7690,DAT_004d7924,0xe2,DAT_004d7908,iVar6);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        iVar6 = DAT_004d76a4;
        if (local_34 != 0) {
          iVar6 = local_34;
        }
        compress_log_output(0x4400000,DAT_004d790c,DAT_004d790c,iVar6);
      }
      file_heap_free(iVar4);
      uVar5 = 0x2b;
    }
    else {
      iVar6 = Thread_MsgPbNotifyByBle(1,4,iVar4,local_38 & 0xffff);
      if (iVar6 == 0) {
        file_heap_free(iVar4);
        uVar5 = 0;
      }
      else {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004d7694,DAT_004d7690,DAT_004d7924,0xe8,DAT_004d7938);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004d793c,DAT_004d793c);
        }
        file_heap_free(iVar4);
        uVar5 = 0xffffffff;
      }
    }
  }
  return uVar5;
}

