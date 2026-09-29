
undefined4 APP_PbTxEncodeQuicklistItem(undefined1 param_1,undefined4 *param_2)

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
  
  uVar4 = DAT_005595fc;
  if (param_2 == (undefined4 *)0x0) {
    FUN_00439c04(auStack_40,DAT_005595ec,0x14);
    local_3c = 1;
    APP_errorFaultHandler(auStack_40);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00559194,DAT_0055936c,DAT_005595f4,0xa7,DAT_005595f0);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005595f8);
    }
    uVar4 = 2;
  }
  else {
    FUN_004905f4(auStack_2c,DAT_005595fc,0x400);
    FUN_00439c04(auStack_54,auStack_2c,0x14);
    puVar1 = DAT_00559600;
    FUN_0043c0e4(DAT_00559600,0x1238,0);
    *puVar1 = 1;
    puVar1[1] = param_1;
    *(undefined2 *)(puVar1 + 2) = 3;
    *(undefined4 *)(puVar1 + 8) = *param_2;
    *(undefined4 *)(puVar1 + 0xc) = param_2[1];
    *(undefined4 *)(puVar1 + 0x10) = param_2[2];
    puVar1[0xec] = 0;
    cVar2 = FUN_00490c32(auStack_54,DAT_005591a8,puVar1);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00559194,DAT_0055936c,DAT_005595f4,0xbd,DAT_00559604,local_48 & 0xffff);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00559608,DAT_00559608,local_48 & 0xffff);
    }
    if (cVar2 == '\0') {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        iVar3 = DAT_00559434;
        if (local_44 != 0) {
          iVar3 = local_44;
        }
        FUN_0043d574(1,DAT_00559194,DAT_0055936c,DAT_005595f4,0xc0,DAT_0055977c,iVar3);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        iVar3 = DAT_00559434;
        if (local_44 != 0) {
          iVar3 = local_44;
        }
        compress_log_output(0x4400000,DAT_00559780,DAT_00559780,iVar3);
      }
      uVar4 = 0x2b;
    }
    else {
      Thread_MsgPbTxByBle(1,0xc,uVar4,local_48 & 0xffff);
      uVar4 = 0;
    }
  }
  return uVar4;
}

