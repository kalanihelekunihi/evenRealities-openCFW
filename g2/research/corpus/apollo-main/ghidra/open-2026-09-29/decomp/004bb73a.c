
undefined4 PB_TxEncodeNotifySecAuthImpl(int param_1)

{
  char cVar1;
  ushort uVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  undefined1 auStack_3c [12];
  uint local_30;
  int local_2c;
  undefined1 auStack_28 [20];
  
  if (*DAT_004bc188 == '\0') {
    uVar3 = 0;
  }
  else {
    iVar4 = file_heap_allocate(0x1a8);
    if (iVar4 == 0) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004bbda8,DAT_004bbda4,DAT_004bc198,0x8c,DAT_004bc194);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004bc19c,DAT_004bc19c);
      }
      uVar3 = 2;
    }
    else {
      FUN_0043c0e4(iVar4,0x1a8,0);
      FUN_004905f4(auStack_28,iVar4,0xd4);
      FUN_00439c04(auStack_3c,auStack_28,0x14);
      *(undefined1 *)(iVar4 + 0xd4) = 4;
      uVar2 = osKernelGetTickCount();
      *(ushort *)(iVar4 + 0xd6) = uVar2 & 0xff;
      *(undefined2 *)(iVar4 + 0xd8) = 3;
      *(bool *)(iVar4 + 0xdc) = param_1 != 0;
      *(undefined1 *)(iVar4 + 0xde) = 0;
      cVar1 = FUN_00490c32(auStack_3c,DAT_004bbfa8,(undefined1 *)(iVar4 + 0xd4));
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004bbda8,DAT_004bbda4,DAT_004bc198,0x9e,DAT_004bc1a0,local_30);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004bc1a4,DAT_004bc1a4,local_30);
      }
      if (cVar1 == '\0') {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          iVar5 = DAT_004bbfb4;
          if (local_2c != 0) {
            iVar5 = local_2c;
          }
          FUN_0043d574(1,DAT_004bbda8,DAT_004bbda4,DAT_004bc198,0xa1,DAT_004bbfb8,iVar5);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          iVar5 = DAT_004bbfb4;
          if (local_2c != 0) {
            iVar5 = local_2c;
          }
          compress_log_output(0x4400000,DAT_004bc190,DAT_004bc190,iVar5);
        }
        file_heap_free(iVar4);
        uVar3 = 0x2b;
      }
      else {
        iVar5 = Thread_MsgPbNotifyByBleDirect(1,0x80,iVar4,local_30 & 0xffff);
        if (iVar5 == 0) {
          file_heap_free(iVar4);
          uVar3 = 0;
        }
        else {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(1,DAT_004bbda8,DAT_004bbda4,DAT_004bc198,0xa7,DAT_004bc1a8);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_004bc5a4,DAT_004bc5a4);
          }
          file_heap_free(iVar4);
          uVar3 = 0xffffffff;
        }
      }
    }
  }
  return uVar3;
}

