
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0059f0ea(int param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  char cVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  
  uVar6 = param_3;
  FUN_0059eb0e();
  iVar2 = _DAT_0059f4bc;
  pcVar1 = _DAT_0059f4b8;
  if (param_1 == 0) {
    cVar3 = APP_PbTranslateRxFrameDataProcess(param_2,param_3 & 0xffff,_DAT_0059f4bc);
    *pcVar1 = cVar3;
    if (*pcVar1 == '\r') {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0059f414,DAT_0059f410,PTR_s_Translate_common_data_handler_0059f4c4,0x107,
                     PTR_s_translate_duplicate_packet__igno_0059f4c0,uVar6,param_4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__translate_translate_duplicate_p_0059f4c8,
                            PTR_s__translate_translate_duplicate_p_0059f4c8);
      }
      *pcVar1 = '\0';
      APP_PbTranslateTxEncodeCommResp(pcVar1,*(undefined1 *)(iVar2 + 1));
    }
    else if (*pcVar1 == '\0') {
      iVar4 = FUN_0059edba(iVar2);
      if (iVar4 == 0) {
        *pcVar1 = '\0';
        APP_PbTranslateTxEncodeCommResp(pcVar1,*(undefined1 *)(iVar2 + 1));
        FUN_0059ed06();
      }
      else {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(2,DAT_0059f414,DAT_0059f410,PTR_s_Translate_common_data_handler_0059f4c4,
                       0x114,PTR_s_translate_data_recv_handler_fail_0059f4d4,iVar4,param_4);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__translate_translate_data_recv_h_0059f4d8,
                              PTR_s__translate_translate_data_recv_h_0059f4d8,iVar4);
        }
        *pcVar1 = '\a';
        APP_PbTranslateTxEncodeCommResp(pcVar1,*(undefined1 *)(iVar2 + 1));
      }
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0059f414,DAT_0059f410,PTR_s_Translate_common_data_handler_0059f4c4,0x10d,
                     PTR_s_translate_error___d__send_error_r_0059f4cc,*pcVar1,param_4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__translate_translate_error___d__s_0059f4d0,
                            PTR_s__translate_translate_error___d__s_0059f4d0,*pcVar1);
      }
      *pcVar1 = '\a';
      APP_PbTranslateTxEncodeCommResp(pcVar1,*(undefined1 *)(iVar2 + 1));
    }
  }
  FUN_0059ebc8();
  return 0;
}

