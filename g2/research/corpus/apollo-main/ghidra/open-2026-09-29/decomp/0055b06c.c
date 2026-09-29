
undefined4 APP_PbTxEncodeHealthMultHighlight(undefined1 param_1,ushort *param_2)

{
  undefined1 *puVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 auStack_54 [12];
  uint local_48;
  int local_44;
  undefined1 auStack_40 [4];
  undefined2 local_3c;
  undefined1 auStack_2c [20];
  
  uVar4 = DAT_0055b260;
  if (param_2 == (ushort *)0x0) {
    FUN_00439c04(auStack_40,DAT_0055b288,0x14);
    local_3c = 1;
    APP_errorFaultHandler(auStack_40);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0055b238,DAT_0055b234,DAT_0055b28c,400,DAT_0055b22c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0055b23c);
    }
    uVar4 = 2;
  }
  else {
    FUN_004905f4(auStack_2c,DAT_0055b260,0x100);
    FUN_00439c04(auStack_54,auStack_2c,0x14);
    puVar1 = DAT_0055b264;
    FUN_0043c0e4(DAT_0055b264,0x31c,0);
    *puVar1 = 4;
    puVar1[1] = param_1;
    *(undefined2 *)(puVar1 + 2) = 6;
    *(ushort *)(puVar1 + 4) = *param_2;
    for (iVar3 = 0; iVar3 < (int)(uint)*param_2; iVar3 = iVar3 + 1) {
      puVar1[iVar3 * 0x106 + 6] = (char)param_2[iVar3 * 0x83 + 1];
      puVar1[iVar3 * 0x106 + 0x10a] = (char)param_2[iVar3 * 0x83 + 0x83];
    }
    puVar1[0x318] = 0;
    cVar2 = FUN_00490c32(auStack_54,DAT_0055b224,puVar1);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0055b238,DAT_0055b234,DAT_0055b28c,0x1ad,DAT_0055b290,local_48 & 0xffff);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0055b294,DAT_0055b294,local_48 & 0xffff);
    }
    if (cVar2 == '\0') {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        iVar3 = DAT_0055b298;
        if (local_44 != 0) {
          iVar3 = local_44;
        }
        FUN_0043d574(1,DAT_0055b238,DAT_0055b234,DAT_0055b28c,0x1b0,DAT_0055b29c,iVar3);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        iVar3 = DAT_0055b298;
        if (local_44 != 0) {
          iVar3 = local_44;
        }
        compress_log_output(0x4400000,DAT_0055b2a0,DAT_0055b2a0,iVar3);
      }
      uVar4 = 0x2b;
    }
    else {
      Thread_MsgPbTxByBle(1,0xe,uVar4,local_48 & 0xffff);
      uVar4 = 0;
    }
  }
  return uVar4;
}

