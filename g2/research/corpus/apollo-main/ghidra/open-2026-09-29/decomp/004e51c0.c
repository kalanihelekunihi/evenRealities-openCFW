
undefined4 APP_PbTxEncodeEvenAIConfig(undefined1 param_1,undefined1 *param_2)

{
  undefined1 *puVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 auStack_54 [12];
  uint uStack_48;
  int iStack_44;
  undefined1 auStack_40 [4];
  undefined2 uStack_3c;
  undefined1 auStack_2c [20];
  
  uVar4 = DAT_004e5454;
  if (param_2 == (undefined1 *)0x0) {
    FUN_00439c04(auStack_40,PTR_DAT_004e54a4,0x14);
    uStack_3c = 1;
    APP_errorFaultHandler(auStack_40);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_pb_evenai_004e54b0,PTR_s_D__01_workspace_s200_ap510b_iar__004e54ac,
                   PTR_s_APP_PbTxEncodeEvenAIConfig_004e54a8,0x351,PTR_s_PORINT_NULL_004e5494);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__pb_evenai_PORINT_NULL_004e54b4);
    }
    uVar4 = 2;
  }
  else {
    FUN_004905f4(auStack_2c,DAT_004e5454,0x100);
    FUN_00439c04(auStack_54,auStack_2c,0x14);
    puVar1 = DAT_004e5458;
    FUN_0043c0e4(DAT_004e5458,0x20c,0);
    *puVar1 = 10;
    puVar1[1] = param_1;
    *(undefined2 *)(puVar1 + 2) = 0xd;
    puVar1[4] = *param_2;
    puVar1[5] = param_2[1];
    puVar1[6] = 0;
    puVar1[7] = param_2[3];
    cVar2 = FUN_00490c32(auStack_54,PTR_DAT_004e54b8,puVar1);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_pb_evenai_004e54b0,PTR_s_D__01_workspace_s200_ap510b_iar__004e54ac,
                   PTR_s_APP_PbTxEncodeEvenAIConfig_004e54a8,0x367,DAT_004e545c,uStack_48 & 0xffff);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004e5460,DAT_004e5460,uStack_48 & 0xffff);
    }
    if (cVar2 == '\0') {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        iVar3 = DAT_004e5464;
        if (iStack_44 != 0) {
          iVar3 = iStack_44;
        }
        FUN_0043d574(1,PTR_s_pb_evenai_004e54b0,PTR_s_D__01_workspace_s200_ap510b_iar__004e54ac,
                     PTR_s_APP_PbTxEncodeEvenAIConfig_004e54a8,0x36a,DAT_004e5468,iVar3);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        iVar3 = DAT_004e5464;
        if (iStack_44 != 0) {
          iVar3 = iStack_44;
        }
        compress_log_output(0x4400000,PTR_s__pb_evenai_Encoding_failed___s_004e548c,
                            PTR_s__pb_evenai_Encoding_failed___s_004e548c,iVar3);
      }
      uVar4 = 0x2b;
    }
    else {
      Thread_MsgPbTxByBle(1,7,uVar4,uStack_48 & 0xffff);
      uVar4 = 0;
    }
  }
  return uVar4;
}

