
undefined4
APP_PbNotifyEncodeQuicklistEvent
          (undefined4 param_1,undefined1 *param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  undefined1 *puVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  undefined1 auStack_54 [12];
  uint local_48;
  int local_44;
  undefined1 auStack_40 [4];
  undefined2 local_3c;
  undefined1 auStack_2c [20];
  undefined4 uStack_18;
  
  uVar5 = DAT_005597e0;
  uStack_18 = param_4;
  if (param_2 == (undefined1 *)0x0) {
    FUN_00439c04(auStack_40,DAT_005597d0,0x14);
    local_3c = 1;
    APP_errorFaultHandler(auStack_40);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005597cc,DAT_005597c8,DAT_005597d8,0x17e,DAT_005597d4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005597dc);
    }
    uVar5 = 2;
  }
  else {
    FUN_004905f4(auStack_2c,DAT_005597e0,0x400);
    FUN_00439c04(auStack_54,auStack_2c,0x14);
    puVar2 = DAT_005597e4;
    FUN_0043c0e4(DAT_005597e4,0x1238,0);
    *puVar2 = 3;
    pcVar1 = DAT_00559784;
    puVar2[1] = *DAT_00559784;
    *pcVar1 = *pcVar1 + '\x01';
    *(undefined2 *)(puVar2 + 2) = 5;
    puVar2[8] = *param_2;
    *(undefined4 *)(puVar2 + 0xc) = *(undefined4 *)(param_2 + 4);
    cVar3 = FUN_00490c32(auStack_54,DAT_005597a8,puVar2);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005597cc,DAT_005597c8,DAT_005597d8,0x192,DAT_005597e8,local_48 & 0xffff);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_005597ec,DAT_005597ec,local_48 & 0xffff);
    }
    if (cVar3 == '\0') {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        iVar4 = DAT_005597ac;
        if (local_44 != 0) {
          iVar4 = local_44;
        }
        FUN_0043d574(1,DAT_005597cc,DAT_005597c8,DAT_005597d8,0x195,DAT_0055977c,iVar4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        iVar4 = DAT_005597ac;
        if (local_44 != 0) {
          iVar4 = local_44;
        }
        compress_log_output(0x4400000,DAT_00559780,DAT_00559780,iVar4);
      }
      uVar5 = 0x2b;
    }
    else {
      Thread_MsgPbNotifyByBle(1,0xc,uVar5,local_48 & 0xffff);
      uVar5 = 0;
    }
  }
  return uVar5;
}

