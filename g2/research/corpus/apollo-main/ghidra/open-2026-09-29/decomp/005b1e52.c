
undefined4 APP_PbConversateTxEncodePrepNoteListRequest(void)

{
  undefined1 *puVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 auStack_34 [12];
  uint local_28;
  int local_24;
  undefined1 auStack_20 [20];
  
  puVar1 = DAT_005b2288;
  FUN_0043c0e4(DAT_005b2288,0xfac,0);
  *puVar1 = 2;
  puVar1[1] = *DAT_005b2264 + '\x01';
  *(undefined2 *)(puVar1 + 2) = 4;
  puVar1[4] = 0;
  uVar4 = DAT_005b228c;
  FUN_004905f4(auStack_20,DAT_005b228c,0x100);
  FUN_00439c04(auStack_34,auStack_20,0x14);
  cVar2 = FUN_00490c32(auStack_34,DAT_005b2254,puVar1);
  if (cVar2 == '\0') {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      iVar3 = DAT_005b2258;
      if (local_24 != 0) {
        iVar3 = local_24;
      }
      FUN_0043d574(1,DAT_005b2248,DAT_005b2244,DAT_005b2298,0x87,DAT_005b2290,iVar3);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      iVar3 = DAT_005b2258;
      if (local_24 != 0) {
        iVar3 = local_24;
      }
      compress_log_output(0x4400000,DAT_005b2294,DAT_005b2294,iVar3);
    }
    uVar4 = 5;
  }
  else {
    iVar3 = FUN_0045a568();
    if (iVar3 == 1) {
      Thread_MsgPbNotifyByBle(1,0xb,uVar4,local_28 & 0xffff);
    }
    uVar4 = 0;
  }
  return uVar4;
}

