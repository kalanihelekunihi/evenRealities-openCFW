
undefined4 APP_PbTxEncodeHealthSingleData(undefined1 param_1,undefined1 *param_2)

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
  
  uVar4 = DAT_0055ad70;
  if (param_2 == (undefined1 *)0x0) {
    FUN_00439c04(auStack_40,DAT_0055ad68,0x14);
    local_3c = 1;
    APP_errorFaultHandler(auStack_40);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_pb_health_0055ab9c,DAT_0055abb8,DAT_0055ad6c,0x86,DAT_0055abcc);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0055abd4);
    }
    uVar4 = 2;
  }
  else {
    FUN_004905f4(auStack_2c,DAT_0055ad70,0x100);
    FUN_00439c04(auStack_54,auStack_2c,0x14);
    puVar1 = DAT_0055ad74;
    FUN_0043c0e4(DAT_0055ad74,0x31c,0);
    *puVar1 = 1;
    puVar1[1] = param_1;
    *(undefined2 *)(puVar1 + 2) = 3;
    puVar1[4] = *param_2;
    *(undefined4 *)(puVar1 + 8) = *(undefined4 *)(param_2 + 4);
    *(undefined4 *)(puVar1 + 0xc) = *(undefined4 *)(param_2 + 8);
    *(undefined4 *)(puVar1 + 0x10) = *(undefined4 *)(param_2 + 0xc);
    *(undefined4 *)(puVar1 + 0x14) = *(undefined4 *)(param_2 + 0x10);
    puVar1[0x19] = param_2[0x15];
    puVar1[0x18] = 0;
    cVar2 = FUN_00490c32(auStack_54,DAT_0055abb0,puVar1);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_pb_health_0055ab9c,DAT_0055abb8,DAT_0055ad6c,0x9f,DAT_0055af04,
                   local_48 & 0xffff);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0055af08,DAT_0055af08,local_48 & 0xffff);
    }
    if (cVar2 == '\0') {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        puVar5 = PTR_s__none__0055abbc;
        if (local_44 != (undefined *)0x0) {
          puVar5 = local_44;
        }
        FUN_0043d574(1,PTR_s_pb_health_0055ab9c,DAT_0055abb8,DAT_0055ad6c,0xa2,DAT_0055af0c,puVar5);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        puVar5 = PTR_s__none__0055abbc;
        if (local_44 != (undefined *)0x0) {
          puVar5 = local_44;
        }
        compress_log_output(0x4400000,DAT_0055b058,DAT_0055b058,puVar5);
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

