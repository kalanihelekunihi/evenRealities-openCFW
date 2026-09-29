
undefined4 PB_TxEncodeNotifyRingConnectInfoImpl(undefined1 param_1)

{
  undefined1 uVar1;
  char cVar2;
  ushort uVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  undefined1 auStack_3c [12];
  uint local_30;
  int local_2c;
  undefined1 auStack_28 [20];
  
  iVar4 = file_heap_allocate(0x1a8);
  if (iVar4 == 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004bc7a4,DAT_004bc7a0,DAT_004bcb08,0x19c,DAT_004bc934);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004bc938,DAT_004bc938);
    }
    uVar5 = 2;
  }
  else {
    FUN_0043c0e4(iVar4,0x1a8,0);
    FUN_004905f4(auStack_28,iVar4,0xd4);
    FUN_00439c04(auStack_3c,auStack_28,0x14);
    *(undefined1 *)(iVar4 + 0xd4) = 6;
    uVar3 = osKernelGetTickCount();
    *(ushort *)(iVar4 + 0xd6) = uVar3 & 0xff;
    *(undefined2 *)(iVar4 + 0xd8) = 5;
    target_addr_name_copy_004a2190(iVar4 + 0xe0,iVar4 + 0xe8);
    uVar1 = auth_mode_set(0x5a);
    *(undefined1 *)(iVar4 + 0xdc) = uVar1;
    auth_mode_set(0);
    *(undefined1 *)(iVar4 + 0xf8) = param_1;
    if (*(char *)(iVar4 + 0xf8) == '\0') {
      APP_MasterClearRingConnectFailureNotifyAfterRetry();
    }
    else {
      FUN_004b82e8(2);
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004bc7a4,DAT_004bc7a0,DAT_004bcb08,0x1b5,DAT_004bcb0c,
                   *(undefined1 *)(iVar4 + 0xf8));
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004bcb10,DAT_004bcb10,*(undefined1 *)(iVar4 + 0xf8));
    }
    *(undefined1 *)(iVar4 + 0xf9) = 0;
    cVar2 = FUN_00490c32(auStack_3c,DAT_004bc920,(undefined1 *)(iVar4 + 0xd4));
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004bc7a4,DAT_004bc7a0,DAT_004bcb08,0x1bb,DAT_004bc924,local_30);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004bc928,DAT_004bc928,local_30);
    }
    if (cVar2 == '\0') {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        iVar6 = DAT_004bc92c;
        if (local_2c != 0) {
          iVar6 = local_2c;
        }
        FUN_0043d574(1,DAT_004bc7a4,DAT_004bc7a0,DAT_004bcb08,0x1be,DAT_004bc930,iVar6);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        iVar6 = DAT_004bc92c;
        if (local_2c != 0) {
          iVar6 = local_2c;
        }
        compress_log_output(0x4400000,DAT_004bcb04,DAT_004bcb04,iVar6);
      }
      file_heap_free(iVar4);
      uVar5 = 0x2b;
    }
    else {
      iVar6 = Thread_MsgPbNotifyByBleDirect(1,0x80,iVar4,local_30 & 0xffff);
      if (iVar6 == 0) {
        file_heap_free(iVar4);
        uVar5 = 0;
      }
      else {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004bc7a4,DAT_004bc7a0,DAT_004bcb08,0x1c4,DAT_004bcb14);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004bcdd8,DAT_004bcdd8);
        }
        file_heap_free(iVar4);
        uVar5 = 0xffffffff;
      }
    }
  }
  return uVar5;
}

