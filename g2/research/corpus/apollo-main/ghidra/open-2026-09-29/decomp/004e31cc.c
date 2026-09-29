
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4
APP_PbRxEvenAIFrameDataProcess(int param_1,ushort param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  undefined *puVar5;
  undefined4 uStack_248;
  undefined *puStack_244;
  undefined *puStack_240;
  undefined1 auStack_23c [12];
  undefined *puStack_230;
  undefined1 auStack_22c [16];
  byte bStack_21c;
  char cStack_21b;
  undefined1 auStack_218 [520];
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  iVar3 = FUN_0043d0ce(0);
  if (iVar3 << 0x1e < 0) {
    puStack_240 = (undefined *)(uint)param_2;
    puStack_244 = PTR_s_len__d__004e3b6c;
    uStack_248 = 0x33;
    FUN_0043d574(4,DAT_004e3d08,DAT_004e3d04,PTR_s_APP_PbRxEvenAIFrameDataProcess_004e3b70);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__pb_evenai_len__d__004e3b74,
                        PTR_s__pb_evenai_len__d__004e3b74,param_2);
  }
  if (param_1 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      puStack_244 = PTR_s_pData_is_NULL_004e3b78;
      uStack_248 = 0x35;
      FUN_0043d574(1,DAT_004e3d08,DAT_004e3d04,PTR_s_APP_PbRxEvenAIFrameDataProcess_004e3b70);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__pb_evenai_pData_is_NULL_004e3b7c,
                          PTR_s__pb_evenai_pData_is_NULL_004e3b7c);
    }
    return 2;
  }
  FUN_0048949c(&bStack_21c,0x20c);
  FUN_0048f49c(auStack_22c,param_1,param_2);
  FUN_00439c04(auStack_23c,auStack_22c,0x10);
  cVar2 = FUN_00490120(auStack_23c,DAT_004e3d0c,&bStack_21c);
  pcVar1 = _DAT_004e3d1c;
  if (cVar2 == '\0') {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      puStack_240 = PTR_s__none__004e3d10;
      if (puStack_230 != (undefined *)0x0) {
        puStack_240 = puStack_230;
      }
      puStack_244 = PTR_s_Decoding_failed___s_004e3d14;
      uStack_248 = 0x3e;
      FUN_0043d574(1,DAT_004e3d08,DAT_004e3d04,PTR_s_APP_PbRxEvenAIFrameDataProcess_004e3b70);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      puVar5 = PTR_s__none__004e3d10;
      if (puStack_230 != (undefined *)0x0) {
        puVar5 = puStack_230;
      }
      compress_log_output(0x4400000,PTR_s__pb_evenai_Decoding_failed___s_004e3d18,
                          PTR_s__pb_evenai_Decoding_failed___s_004e3d18,puVar5);
    }
    return 0x2b;
  }
  if ((*_DAT_004e3d1c == '\x01') && (cStack_21b == _DAT_004e3d1c[1])) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      puStack_240 = (undefined *)(uint)(byte)pcVar1[1];
      puStack_244 = PTR_s_magic_random_is_equal_to_last_ma_004e3d20;
      uStack_248 = 0x45;
      FUN_0043d574(2,DAT_004e3d08,DAT_004e3d04,PTR_s_APP_PbRxEvenAIFrameDataProcess_004e3b70);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8400000,PTR_s__pb_evenai_magic_random_is_equal_004e3d24,
                          PTR_s__pb_evenai_magic_random_is_equal_004e3d24,pcVar1[1]);
    }
    uStack_248._0_2_ = CONCAT11(*PTR_DAT_004e3d28,(undefined1)uStack_248);
    APP_PbTxEncodeEvenAICommResp(cStack_21b,(int)&uStack_248 + 1);
    return 1;
  }
  *_DAT_004e3d1c = '\x01';
  pcVar1[1] = cStack_21b;
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    puStack_240 = (undefined *)(uint)bStack_21c;
    puStack_244 = PTR_s_even_ai_command_id___d_004e3d2c;
    uStack_248 = 0x50;
    FUN_0043d574(4,DAT_004e3d08,DAT_004e3d04,PTR_s_APP_PbRxEvenAIFrameDataProcess_004e3b70);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__pb_evenai_even_ai_command_id____004e3d30,
                        PTR_s__pb_evenai_even_ai_command_id____004e3d30,bStack_21c);
  }
  if (bStack_21c == 1) {
    iVar3 = PB_RxEvenAICtrl(cStack_21b,auStack_218);
    if (iVar3 == 0) {
      uVar4 = APP_PbTxEncodeEvenAICtrl(cStack_21b,auStack_218);
      return uVar4;
    }
  }
  else {
    if (bStack_21c == 0) {
LAB_004e351a:
      uStack_248 = CONCAT31(uStack_248._1_3_,*_DAT_004e4108);
      uVar4 = APP_PbTxEncodeEvenAICommResp(cStack_21b,&uStack_248);
      return uVar4;
    }
    if (bStack_21c == 3) {
      iVar3 = PB_RxEvenAIAskInfo(cStack_21b,auStack_218);
      if (iVar3 == 0) {
        uVar4 = APP_PbTxEncodeEvenAIAskInfo(cStack_21b,auStack_218);
        return uVar4;
      }
    }
    else if (bStack_21c < 3) {
      iVar3 = PB_RxEvenAIVADInfo(cStack_21b,auStack_218);
      if (iVar3 == 0) {
        uVar4 = APP_PbTxEncodeEvenAIVADInfo(cStack_21b,auStack_218);
        return uVar4;
      }
    }
    else if (bStack_21c == 5) {
      iVar3 = PB_RxEvenAIReplyInfo(cStack_21b,auStack_218);
      if (iVar3 == 0) {
        uVar4 = APP_PbTxEncodeEvenAIReplyInfo(cStack_21b,auStack_218);
        return uVar4;
      }
    }
    else if (bStack_21c < 5) {
      iVar3 = PB_RxEvenAIAnalyseInfo(cStack_21b,auStack_218);
      if (iVar3 == 0) {
        uVar4 = APP_PbTxEncodeEvenAIAnalyseInfo(cStack_21b,auStack_218);
        return uVar4;
      }
    }
    else if (bStack_21c == 7) {
      iVar3 = PB_RxEvenAIPromptInfo(cStack_21b,auStack_218);
      if (iVar3 == 0) {
        uVar4 = APP_PbTxEncodeEvenAIPromptInfo(cStack_21b,auStack_218);
        return uVar4;
      }
    }
    else if (bStack_21c < 7) {
      iVar3 = PB_RxEvenAISkillInfo(cStack_21b,auStack_218);
      if (iVar3 == 0) {
        uVar4 = APP_PbTxEncodeEvenAISkillInfo(cStack_21b,auStack_218);
        return uVar4;
      }
    }
    else if (bStack_21c == 9) {
      iVar3 = PB_RxEvenAIHeartbeat(cStack_21b,auStack_218);
      if (iVar3 == 0) {
        uVar4 = APP_PbTxEncodeEvenAIHeartbeat(cStack_21b,auStack_218);
        return uVar4;
      }
    }
    else if (bStack_21c < 9) {
      iVar3 = PB_RxEvenAIEvent(cStack_21b,auStack_218);
      if (iVar3 == 0) {
        uVar4 = APP_PbTxEncodeEvenAIEvent(cStack_21b,auStack_218);
        return uVar4;
      }
    }
    else {
      if (bStack_21c != 10) goto LAB_004e351a;
      iVar3 = PB_RxEvenAIConfig(cStack_21b,auStack_218);
      if (iVar3 == 0) {
        uVar4 = APP_PbTxEncodeEvenAIConfig(cStack_21b,auStack_218);
        return uVar4;
      }
    }
  }
  return 1;
}

