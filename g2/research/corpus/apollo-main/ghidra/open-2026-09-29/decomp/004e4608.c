
undefined4 APP_PbTxEncodeEvenAISkillInfo(undefined1 param_1,int param_2)

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
  
  uVar4 = DAT_004e4a24;
  if (param_2 == 0) {
    FUN_00439c04(auStack_40,PTR_DAT_004e4e58,0x14);
    uStack_3c = 1;
    APP_errorFaultHandler(auStack_40);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004e487c,DAT_004e4878,PTR_s_APP_PbTxEncodeEvenAISkillInfo_004e4f24,0x228,
                   DAT_004e4870);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004e4880);
    }
    uVar4 = 2;
  }
  else {
    FUN_004905f4(auStack_2c,DAT_004e4a24,0x100);
    FUN_00439c04(auStack_54,auStack_2c,0x14);
    puVar1 = DAT_004e4a28;
    FUN_0043c0e4(DAT_004e4a28,0x20c,0);
    *puVar1 = 6;
    puVar1[1] = param_1;
    *(undefined2 *)(puVar1 + 2) = 8;
    puVar1[5] = *(undefined1 *)(param_2 + 1);
    puVar1[0x10e] = 0;
    cVar2 = FUN_00490c32(auStack_54,DAT_004e4884,puVar1);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004e487c,DAT_004e4878,PTR_s_APP_PbTxEncodeEvenAISkillInfo_004e4f24,0x23c,
                   DAT_004e4a2c,uStack_48 & 0xffff);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004e4a30,DAT_004e4a30,uStack_48 & 0xffff);
    }
    if (cVar2 == '\0') {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        iVar3 = DAT_004e4b08;
        if (iStack_44 != 0) {
          iVar3 = iStack_44;
        }
        FUN_0043d574(1,DAT_004e487c,DAT_004e4878,PTR_s_APP_PbTxEncodeEvenAISkillInfo_004e4f24,0x23f,
                     DAT_004e4b0c,iVar3);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        iVar3 = DAT_004e4b08;
        if (iStack_44 != 0) {
          iVar3 = iStack_44;
        }
        compress_log_output(0x4400000,PTR_s__pb_evenai_Encoding_failed___s_004e4f20,
                            PTR_s__pb_evenai_Encoding_failed___s_004e4f20,iVar3);
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

