
undefined4
APP_PbNotifyEncodeEvenAICtrl
          (undefined4 param_1,undefined1 *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  char *pcVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  undefined *puVar6;
  undefined1 auStack_54 [12];
  uint local_48;
  undefined *local_44;
  undefined1 auStack_40 [4];
  undefined2 local_3c;
  undefined1 auStack_2c [20];
  undefined4 uStack_18;
  
  uVar5 = DAT_004e4034;
  uStack_18 = param_4;
  if (param_2 == (undefined1 *)0x0) {
    FUN_00439c04(auStack_40,DAT_004e411c,0x14);
    local_3c = 1;
    APP_errorFaultHandler(auStack_40);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004e3d08,DAT_004e3d04,DAT_004e4120,0xee,DAT_004e3e8c);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__pb_evenai_PORINT_NULL_004e3e94);
    }
    uVar5 = 2;
  }
  else {
    FUN_004905f4(auStack_2c,DAT_004e4034,0x100);
    FUN_00439c04(auStack_54,auStack_2c,0x14);
    puVar1 = DAT_004e4038;
    FUN_0043c0e4(DAT_004e4038,0x20c,0);
    *puVar1 = 1;
    pcVar2 = DAT_004e4124;
    puVar1[1] = *DAT_004e4124;
    *pcVar2 = *pcVar2 + '\x01';
    *(undefined2 *)(puVar1 + 2) = 3;
    puVar1[4] = *param_2;
    cVar3 = FUN_00490c32(auStack_54,DAT_004e3d0c,puVar1);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004e3d08,DAT_004e3d04,DAT_004e4120,0x101,DAT_004e4110,local_48 & 0xffff);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004e4114,DAT_004e4114,local_48 & 0xffff);
    }
    if (cVar3 == '\0') {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        puVar6 = PTR_s__none__004e3d10;
        if (local_44 != (undefined *)0x0) {
          puVar6 = local_44;
        }
        FUN_0043d574(1,DAT_004e3d08,DAT_004e3d04,DAT_004e4120,0x104,DAT_004e4118,puVar6);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        puVar6 = PTR_s__none__004e3d10;
        if (local_44 != (undefined *)0x0) {
          puVar6 = local_44;
        }
        compress_log_output(0x4400000,DAT_004e4388,DAT_004e4388,puVar6);
      }
      uVar5 = 0x2b;
    }
    else {
      Thread_MsgPbNotifyByBle(1,7,uVar5,local_48 & 0xffff);
      uVar5 = 0;
    }
  }
  return uVar5;
}

