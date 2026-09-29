
undefined4 APP_PbTxEncodeEvenAICommResp(undefined1 param_1,undefined1 *param_2)

{
  undefined1 *puVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 auStack_3c [12];
  uint uStack_30;
  int iStack_2c;
  undefined1 auStack_28 [20];
  
  puVar1 = DAT_004e5458;
  FUN_0043c0e4(DAT_004e5458,0x20c,0);
  *puVar1 = 0xa1;
  puVar1[1] = param_1;
  *(undefined2 *)(puVar1 + 2) = 0xc;
  puVar1[4] = *param_2;
  uVar4 = DAT_004e5454;
  FUN_004905f4(auStack_28,DAT_004e5454,0x100);
  FUN_00439c04(auStack_3c,auStack_28,0x14);
  cVar2 = FUN_00490c32(auStack_3c,PTR_DAT_004e54b8,puVar1);
  if (cVar2 == '\0') {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      iVar3 = DAT_004e5464;
      if (iStack_2c != 0) {
        iVar3 = iStack_2c;
      }
      FUN_0043d574(1,PTR_s_pb_evenai_004e54b0,PTR_s_D__01_workspace_s200_ap510b_iar__004e54ac,
                   PTR_s_APP_PbTxEncodeEvenAICommResp_004e54c0,899,
                   PTR_s_Encoding_failed___s_004e54bc,iVar3);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      iVar3 = DAT_004e5464;
      if (iStack_2c != 0) {
        iVar3 = iStack_2c;
      }
      compress_log_output(0x4400000,PTR_s__pb_evenai_Encoding_failed___s_004e54c4,
                          PTR_s__pb_evenai_Encoding_failed___s_004e54c4,iVar3);
    }
    uVar4 = 0x2b;
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_pb_evenai_004e54b0,PTR_s_D__01_workspace_s200_ap510b_iar__004e54ac,
                   PTR_s_APP_PbTxEncodeEvenAICommResp_004e54c0,0x388,DAT_004e545c,uStack_30 & 0xffff
                  );
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004e5460,DAT_004e5460,uStack_30 & 0xffff);
    }
    Thread_MsgPbTxByBle(1,7,uVar4,uStack_30 & 0xffff);
    uVar4 = 0;
  }
  return uVar4;
}

