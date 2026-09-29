
undefined4
terminal_encode_and_send
          (undefined1 param_1,short param_2,undefined4 *param_3,undefined1 param_4,int param_5)

{
  undefined1 *puVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined1 auStack_44 [12];
  uint local_38;
  int local_34;
  undefined1 auStack_30 [20];
  
  puVar1 = DAT_005cf1c0;
  FUN_0043c0e4(DAT_005cf1c0,0x850,0);
  *puVar1 = param_1;
  puVar1[1] = param_4;
  *(short *)(puVar1 + 2) = param_2;
  if (param_2 == 9) {
    *(undefined2 *)(puVar1 + 4) = *(undefined2 *)param_3;
  }
  else if (param_2 == 10) {
    puVar1[4] = *(undefined1 *)param_3;
  }
  else if (param_2 == 0xb) {
    uVar4 = param_3[1];
    *(undefined4 *)(puVar1 + 4) = *param_3;
    *(undefined4 *)(puVar1 + 8) = uVar4;
  }
  else if (param_2 == 0xc) {
    puVar1[4] = *(undefined1 *)param_3;
  }
  else if (param_2 == 0xd) {
    puVar1[4] = *(undefined1 *)param_3;
  }
  else if (param_2 == 0x12) {
    uVar4 = param_3[1];
    *(undefined4 *)(puVar1 + 4) = *param_3;
    *(undefined4 *)(puVar1 + 8) = uVar4;
  }
  else if (param_2 == 0x13) {
    *(undefined4 *)(puVar1 + 4) = *param_3;
  }
  else if (param_2 == 0x14) {
    uVar4 = param_3[1];
    uVar5 = param_3[2];
    *(undefined4 *)(puVar1 + 4) = *param_3;
    *(undefined4 *)(puVar1 + 8) = uVar4;
    *(undefined4 *)(puVar1 + 0xc) = uVar5;
  }
  else if (param_2 == 0x16) {
    puVar1[4] = *(undefined1 *)param_3;
  }
  else if (param_2 == 0x18) {
    *(undefined4 *)(puVar1 + 4) = *param_3;
  }
  else {
    if (param_2 != 0x19) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_005cf1d8,DAT_005cf1d4,DAT_005cf1d0,0x53,DAT_005cf1cc,param_2);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_005cf1dc,DAT_005cf1dc,param_2);
      }
      return 8;
    }
    uVar4 = param_3[1];
    *(undefined4 *)(puVar1 + 4) = *param_3;
    *(undefined4 *)(puVar1 + 8) = uVar4;
  }
  uVar4 = DAT_005cf1c4;
  FUN_004905f4(auStack_30,DAT_005cf1c4,0x878);
  FUN_00439c04(auStack_44,auStack_30,0x14);
  cVar2 = FUN_00490c32(auStack_44,DAT_005cf1c8,puVar1);
  if (cVar2 == '\0') {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      iVar3 = DAT_005cf1e0;
      if (local_34 != 0) {
        iVar3 = local_34;
      }
      FUN_0043d574(1,DAT_005cf1d8,DAT_005cf1d4,DAT_005cf1d0,0x5a,DAT_005cf1e4,iVar3);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      iVar3 = DAT_005cf1e0;
      if (local_34 != 0) {
        iVar3 = local_34;
      }
      compress_log_output(0x4400000,DAT_005cf1e8,DAT_005cf1e8,iVar3);
    }
    uVar4 = 5;
  }
  else {
    if (param_5 == 0) {
      iVar3 = FUN_0045a568();
      if (iVar3 == 1) {
        Thread_MsgPbTxByBle(1,0x30,uVar4,local_38 & 0xffff);
      }
    }
    else {
      iVar3 = FUN_0045a568();
      if (iVar3 == 1) {
        Thread_MsgPbNotifyByBle(1,0x30,uVar4,local_38 & 0xffff);
      }
    }
    uVar4 = 0;
  }
  return uVar4;
}

