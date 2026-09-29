
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_00589fe6(int param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  char cVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  
  uVar6 = param_3;
  FUN_00589a4e();
  iVar2 = _DAT_0058a3ac;
  pcVar1 = _DAT_0058a3a8;
  if (param_1 == 0) {
    cVar3 = APP_PbRxTelepromptFrameDataProcess(param_2,param_3 & 0xffff,_DAT_0058a3ac);
    *pcVar1 = cVar3;
    if (*pcVar1 == '\r') {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0058a320,DAT_0058a31c,PTR_s_Teleprompt_common_data_handler_0058a3b4,0x12a
                     ,PTR_s_teleprompt_duplicate_packet__ign_0058a3b0,uVar6,param_4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__teleprompt_teleprompt_duplicate_0058a3b8,
                            PTR_s__teleprompt_teleprompt_duplicate_0058a3b8);
      }
      *pcVar1 = '\0';
      APP_PbTelepromptTxEncodeCommResp(*(undefined1 *)(iVar2 + 1),pcVar1);
    }
    else if (*pcVar1 == '\0') {
      iVar4 = FUN_00589d74(iVar2);
      if (iVar4 == 0) {
        *pcVar1 = '\0';
        APP_PbTelepromptTxEncodeCommResp(*(undefined1 *)(iVar2 + 1),pcVar1);
        FUN_00589cb4();
      }
      else {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(2,DAT_0058a320,DAT_0058a31c,PTR_s_Teleprompt_common_data_handler_0058a3b4,
                       0x137,PTR_s_teleprompt_data_recv_handler_fai_0058a3c4,iVar4,param_4);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__teleprompt_teleprompt_data_recv_0058a3c8,
                              PTR_s__teleprompt_teleprompt_data_recv_0058a3c8,iVar4);
        }
        *pcVar1 = '\x01';
        APP_PbTelepromptTxEncodeCommResp(*(undefined1 *)(iVar2 + 1),pcVar1);
      }
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0058a320,DAT_0058a31c,PTR_s_Teleprompt_common_data_handler_0058a3b4,0x130
                     ,PTR_s_teleprompt_error___d__send_error_0058a3bc,*pcVar1,param_4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__teleprompt_teleprompt_error___d_0058a3c0,
                            PTR_s__teleprompt_teleprompt_error___d_0058a3c0,*pcVar1);
      }
      *pcVar1 = '\x01';
      APP_PbTelepromptTxEncodeCommResp(*(undefined1 *)(iVar2 + 1),pcVar1);
    }
  }
  FUN_00589b08();
  return 0;
}

