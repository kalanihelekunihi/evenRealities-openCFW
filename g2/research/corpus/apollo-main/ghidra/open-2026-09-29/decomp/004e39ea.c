
undefined4 APP_PbTxEncodeEvenAIVADInfo(undefined1 param_1,undefined1 *param_2)

{
  undefined1 *puVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  undefined *puVar5;
  undefined1 auStack_54 [12];
  uint local_48;
  undefined *local_44;
  undefined1 auStack_40 [4];
  undefined2 local_3c;
  undefined1 auStack_2c [20];
  
  uVar4 = DAT_004e4034;
  if (param_2 == (undefined1 *)0x0) {
    FUN_00439c04(auStack_40,DAT_004e4398,0x14);
    local_3c = 1;
    APP_errorFaultHandler(auStack_40);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004e3d08,DAT_004e3d04,DAT_004e439c,0x125,DAT_004e3e8c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__pb_evenai_PORINT_NULL_004e3e94);
    }
    uVar4 = 2;
  }
  else {
    FUN_004905f4(auStack_2c,DAT_004e4034,0x100);
    FUN_00439c04(auStack_54,auStack_2c,0x14);
    puVar1 = DAT_004e4038;
    FUN_0043c0e4(DAT_004e4038,0x20c,0);
    *puVar1 = 2;
    puVar1[1] = param_1;
    *(undefined2 *)(puVar1 + 2) = 4;
    puVar1[4] = *param_2;
    puVar1[5] = 0;
    cVar2 = FUN_00490c32(auStack_54,DAT_004e3d0c,puVar1);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004e3d08,DAT_004e3d04,DAT_004e439c,0x139,DAT_004e4110,local_48 & 0xffff);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004e4114,DAT_004e4114,local_48 & 0xffff);
    }
    if (cVar2 == '\0') {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        puVar5 = PTR_s__none__004e3d10;
        if (local_44 != (undefined *)0x0) {
          puVar5 = local_44;
        }
        FUN_0043d574(1,DAT_004e3d08,DAT_004e3d04,DAT_004e439c,0x13c,DAT_004e4118,puVar5);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        puVar5 = PTR_s__none__004e3d10;
        if (local_44 != (undefined *)0x0) {
          puVar5 = local_44;
        }
        compress_log_output(0x4400000,DAT_004e4388,DAT_004e4388,puVar5);
      }
      uVar4 = 0x2b;
    }
    else {
      Thread_MsgPbTxByBle(1,7,uVar4,local_48 & 0xffff);
      uVar4 = 0;
    }
  }
  return uVar4;
}

