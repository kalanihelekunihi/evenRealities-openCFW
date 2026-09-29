
undefined4 APP_PbConversateTxEncodeCommResp(undefined1 *param_1,undefined1 param_2)

{
  undefined1 *puVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 auStack_3c [12];
  uint local_30;
  int local_2c;
  undefined1 auStack_28 [20];
  
  puVar1 = DAT_005b2288;
  if (param_1 == (undefined1 *)0x0) {
    iVar3 = FUN_0043d0ce(0);
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005b2248,DAT_005b2244,DAT_005b22a4,0xb1,DAT_005b22a0);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005b22a8);
    }
    uVar4 = 6;
  }
  else {
    FUN_0043c0e4(DAT_005b2288,0xfac,0);
    *puVar1 = 0xa2;
    puVar1[1] = param_2;
    *(undefined2 *)(puVar1 + 2) = 10;
    puVar1[4] = *param_1;
    uVar4 = DAT_005b228c;
    FUN_004905f4(auStack_28,DAT_005b228c,0x100);
    FUN_00439c04(auStack_3c,auStack_28,0x14);
    cVar2 = FUN_00490c32(auStack_3c,DAT_005b2254,puVar1);
    if (cVar2 == '\0') {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        iVar3 = DAT_005b2258;
        if (local_2c != 0) {
          iVar3 = local_2c;
        }
        FUN_0043d574(1,DAT_005b2248,DAT_005b2244,DAT_005b22a4,0xbe,DAT_005b2290,iVar3);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        iVar3 = DAT_005b2258;
        if (local_2c != 0) {
          iVar3 = local_2c;
        }
        compress_log_output(0x4400000,DAT_005b2294,DAT_005b2294,iVar3);
      }
      uVar4 = 5;
    }
    else {
      FUN_0043dacc(DAT_005b22ac,0x10,uVar4,local_30 & 0xffff);
      iVar3 = FUN_0045a568();
      if (iVar3 == 1) {
        Thread_MsgPbTxByBle(1,0xb,uVar4,local_30 & 0xffff);
      }
      uVar4 = 0;
    }
  }
  return uVar4;
}

