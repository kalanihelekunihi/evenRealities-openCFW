
undefined4 APP_PbNotifyEncodeQuicklistMultItems(undefined4 param_1,undefined1 *param_2)

{
  undefined1 *puVar1;
  char *pcVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  undefined1 auStack_54 [12];
  uint local_48;
  int local_44;
  undefined1 auStack_40 [4];
  undefined2 local_3c;
  undefined1 auStack_2c [20];
  
  uVar5 = DAT_005595fc;
  if (param_2 == (undefined1 *)0x0) {
    FUN_00439c04(auStack_40,DAT_005597a0,0x14);
    local_3c = 1;
    APP_errorFaultHandler(auStack_40);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00559468,DAT_0055946c,DAT_005597a4,0x124,DAT_005595f0);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005595f8,DAT_005595f8);
    }
    uVar5 = 2;
  }
  else {
    FUN_004905f4(auStack_2c,DAT_005595fc,0x400);
    FUN_00439c04(auStack_54,auStack_2c,0x14);
    puVar1 = DAT_00559600;
    FUN_0043c0e4(DAT_00559600,0x1238,0);
    *puVar1 = 2;
    pcVar2 = DAT_00559784;
    puVar1[1] = *DAT_00559784;
    *pcVar2 = *pcVar2 + '\x01';
    *(undefined2 *)(puVar1 + 2) = 4;
    puVar1[8] = *param_2;
    puVar1[9] = param_2[1];
    *(undefined2 *)(puVar1 + 10) = *(undefined2 *)(param_2 + 2);
    for (iVar4 = 0; iVar4 < (int)(uint)*(ushort *)(param_2 + 2); iVar4 = iVar4 + 1) {
      FUN_00439be4(puVar1 + iVar4 * 0xe8 + 0x10,param_2 + iVar4 * 0xe8 + 8,0xe8);
    }
    cVar3 = FUN_00490c32(auStack_54,DAT_005597a8,puVar1);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00559468,DAT_0055946c,DAT_005597a4,0x13d,DAT_00559604,local_48 & 0xffff);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00559608,DAT_00559608,local_48 & 0xffff);
    }
    if (cVar3 == '\0') {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        iVar4 = DAT_005597ac;
        if (local_44 != 0) {
          iVar4 = local_44;
        }
        FUN_0043d574(1,DAT_00559468,DAT_0055946c,DAT_005597a4,0x140,DAT_0055977c,iVar4);
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

