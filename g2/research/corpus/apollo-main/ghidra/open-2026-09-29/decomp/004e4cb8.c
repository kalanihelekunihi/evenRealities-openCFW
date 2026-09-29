
undefined4
APP_PbNotifyEncodeEvenAIEvent
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
  
  uVar5 = DAT_004e5454;
  uStack_18 = param_4;
  if (param_2 == (undefined1 *)0x0) {
    FUN_00439c04(auStack_40,DAT_004e546c,0x14);
    local_3c = 1;
    APP_errorFaultHandler(auStack_40);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004e51b4,DAT_004e51b0,PTR_s_APP_PbNotifyEncodeEvenAIEvent_004e5470,0x2dd,
                   DAT_004e50d4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004e51b8);
    }
    uVar5 = 2;
  }
  else {
    FUN_004905f4(auStack_2c,DAT_004e5454,0x100);
    FUN_00439c04(auStack_54,auStack_2c,0x14);
    puVar2 = DAT_004e5458;
    FUN_0043c0e4(DAT_004e5458,0x20c,0);
    *puVar2 = 8;
    pcVar1 = DAT_004e5334;
    puVar2[1] = *DAT_004e5334;
    *pcVar1 = *pcVar1 + '\x01';
    *(undefined2 *)(puVar2 + 2) = 10;
    puVar2[4] = *param_2;
    cVar3 = FUN_00490c32(auStack_54,DAT_004e51bc,puVar2);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004e51b4,DAT_004e51b0,PTR_s_APP_PbNotifyEncodeEvenAIEvent_004e5470,0x2f0,
                   DAT_004e545c,local_48 & 0xffff);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004e5460,DAT_004e5460,local_48 & 0xffff);
    }
    if (cVar3 == '\0') {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        iVar4 = DAT_004e5464;
        if (local_44 != 0) {
          iVar4 = local_44;
        }
        FUN_0043d574(1,DAT_004e51b4,DAT_004e51b0,PTR_s_APP_PbNotifyEncodeEvenAIEvent_004e5470,0x2f3,
                     DAT_004e5468,iVar4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        iVar4 = DAT_004e5464;
        if (local_44 != 0) {
          iVar4 = local_44;
        }
        compress_log_output(0x4400000,PTR_s__pb_evenai_Encoding_failed___s_004e4f20,
                            PTR_s__pb_evenai_Encoding_failed___s_004e4f20,iVar4);
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

