
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void even_ai_ui_reflash(void)

{
  char cVar1;
  byte bVar2;
  char *pcVar3;
  int *piVar4;
  undefined *puVar5;
  undefined *puVar6;
  undefined *puVar7;
  undefined *puVar8;
  undefined *puVar9;
  undefined *puVar10;
  undefined *puVar11;
  undefined *puVar12;
  undefined *puVar13;
  int iVar14;
  uint uVar15;
  undefined4 uVar16;
  undefined4 in_r3;
  undefined *apuStack_61c [129];
  undefined1 auStack_418 [516];
  undefined1 auStack_214 [516];
  undefined4 uStack_10;
  
  piVar4 = _DAT_004e7530;
  uStack_10 = in_r3;
  if (*_DAT_004e7530 == 0) {
    iVar14 = ui_common_api_fn_00509c1c();
    *piVar4 = iVar14;
  }
  pcVar3 = _DAT_004e7504;
  cVar1 = *_DAT_004e7504;
  if (cVar1 == '\x01') {
    if (_DAT_004e7504[1] == '\x01') {
      iVar14 = FUN_0043d0ce();
      if (iVar14 << 0x1e < 0) {
        apuStack_61c[0] = PTR_s_Even_AI_wake_up__showing_listeni_004e7534;
        FUN_0043d574(3,PTR_s_even_ai_ui_004e7514,PTR_s_D__01_workspace_s200_ap510b_iar__004e7510,
                     PTR_s_even_ai_ui_reflash_004e7538,0x806);
      }
      iVar14 = FUN_0043d0ce();
      if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__even_ai_ui_Even_AI_wake_up__sho_004e753c,
                            PTR_s__even_ai_ui_Even_AI_wake_up__sho_004e753c);
      }
    }
    else if (_DAT_004e7504[1] != '\x02') {
      return;
    }
    if (*(char *)(DAT_004e74fc + 0x18) == '\0') {
      even_ai_listening_text_toggle();
    }
    FUN_005537cc(0);
    return;
  }
  if (cVar1 == '\x03') {
    even_ai_hide_listening_text();
    if (pcVar3[10] == '\0') {
      iVar14 = FUN_0043d0ce();
      if (iVar14 << 0x1e < 0) {
        apuStack_61c[0] = PTR_s_Even_AI_ASK__using_streaming_mod_004e7540;
        FUN_0043d574(3,PTR_s_even_ai_ui_004e7514,PTR_s_D__01_workspace_s200_ap510b_iar__004e7510,
                     PTR_s_even_ai_ui_reflash_004e7538,0x86e);
      }
      iVar14 = FUN_0043d0ce();
      if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__even_ai_ui_Even_AI_ASK__using_s_004e7544);
      }
      iVar14 = even_ai_add_question(0x4e6fd0,0);
      if (iVar14 != 0) {
        FUN_005537cc(1);
      }
      *_DAT_004e751c = *(undefined4 *)(DAT_004e74fc + 0x14);
      *_DAT_004e7520 = 1;
      even_ai_stream_init_from_service(1);
      even_ai_stream_on_auto_reflash();
      return;
    }
    iVar14 = FUN_0043d0ce();
    if (iVar14 << 0x1e < 0) {
      apuStack_61c[0] = PTR_s_Even_AI_ASK__using_direct_displa_004e7548;
      FUN_0043d574(3,PTR_s_even_ai_ui_004e7514,PTR_s_D__01_workspace_s200_ap510b_iar__004e7510,
                   PTR_s_even_ai_ui_reflash_004e7538,0x87b);
    }
    iVar14 = FUN_0043d0ce();
    if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__even_ai_ui_Even_AI_ASK__using_d_004e754c,
                          PTR_s__even_ai_ui_Even_AI_ASK__using_d_004e754c);
    }
    FUN_004e1fa6();
    uVar16 = text_stream_pending_text(*_DAT_004e752c);
    iVar14 = even_ai_add_question(uVar16,0);
    if (iVar14 != 0) {
      FUN_005537cc(1);
    }
    FUN_004e1fbe();
    even_ai_layout_refresh();
    return;
  }
  if (cVar1 == '\x04') {
    FUN_005537cc(2);
    if (*(char *)(DAT_004e74fc + 0x18) != '\0') {
      even_ai_gray_question(*(char *)(DAT_004e74fc + 0x18) + -1);
      return;
    }
    iVar14 = FUN_0043d0ce();
    if (iVar14 << 0x1e < 0) {
      apuStack_61c[0] = PTR_s_Even_AI_analyse__no_dialog_to_gr_004e7550;
      FUN_0043d574(2,PTR_s_even_ai_ui_004e7514,PTR_s_D__01_workspace_s200_ap510b_iar__004e7510,
                   PTR_s_even_ai_ui_reflash_004e7538,0x896);
    }
    iVar14 = FUN_0043d0ce();
    if ((-1 < iVar14 << 0x1f) && (iVar14 = FUN_0043d0ce(), -1 < iVar14 << 0x1d)) {
      return;
    }
    compress_log_output(0x8000000,PTR_s__even_ai_ui_Even_AI_analyse__no_d_004e7554,
                        PTR_s__even_ai_ui_Even_AI_analyse__no_d_004e7554);
    return;
  }
  if (cVar1 == '\x05') {
    even_ai_hide_listening_text();
    iVar14 = FUN_00553d28();
    if (iVar14 != 3) {
      FUN_005537cc(3);
    }
    if (*(char *)(DAT_004e74fc + 0x18) != '\0') {
      even_ai_gray_question(*(char *)(DAT_004e74fc + 0x18) + -1);
    }
    even_ai_answer_text_reflash();
    return;
  }
  if (cVar1 == '\x06') {
    even_ai_hide_listening_text();
    if (*(char *)(DAT_004e74fc + 0x18) != '\0') {
      even_ai_gray_question(*(char *)(DAT_004e74fc + 0x18) + -1);
    }
    uVar15 = (uint)(byte)pcVar3[1];
    if (uVar15 == 1) {
      if (pcVar3[9] == '\x01') {
        FUN_005537cc(0);
      }
      else {
        FUN_0055389a();
      }
      if (*(short *)(pcVar3 + 0xe) != 0) {
        FUN_0043c0e4(auStack_214,0x201,0);
        FUN_00439be4(auStack_214,pcVar3 + 0x10,*(undefined2 *)(pcVar3 + 0xe));
      }
      even_ai_add_answer(auStack_214,PTR_DAT_004e7558,*(uint *)(pcVar3 + 4) & 0xff,1,0);
      even_ai_layout_refresh();
      service_even_ai_fn_00498310(2);
      return;
    }
    if (uVar15 == 3) {
      if (pcVar3[9] == '\x01') {
        FUN_005537cc(0);
      }
      else {
        FUN_0055389a();
      }
      if (*(short *)(pcVar3 + 0xe) != 0) {
        FUN_0043c0e4(auStack_418,0x201,0);
        FUN_00439be4(auStack_418,pcVar3 + 0x10,*(undefined2 *)(pcVar3 + 0xe));
      }
      even_ai_add_answer(auStack_418,PTR_DAT_004e755c,0xff,1,1);
      even_ai_layout_refresh();
      service_even_ai_fn_00498310(2);
      return;
    }
    if (3 < uVar15 - 4) {
      if (uVar15 - 4 != 4) {
        return;
      }
      if (pcVar3[9] == '\x01') {
        FUN_005537cc(0);
      }
      else {
        FUN_0055389a();
      }
      if (*(short *)(pcVar3 + 0xe) != 0) {
        FUN_0043c0e4(apuStack_61c,0x201,0);
        FUN_00439be4(apuStack_61c,pcVar3 + 0x10,*(undefined2 *)(pcVar3 + 0xe));
      }
      even_ai_add_answer(apuStack_61c,PTR_DAT_004e7560,0xff,1,1);
      even_ai_layout_refresh();
      service_even_ai_fn_00498310(2);
      return;
    }
    iVar14 = FUN_00553d28();
    if (iVar14 != 3) {
      FUN_005537cc(3);
    }
    if (*(int *)(pcVar3 + 4) != 0) {
      return;
    }
    even_ai_answer_text_reflash();
    return;
  }
  if (cVar1 != '\a') {
    return;
  }
  if (*(char *)(DAT_004e74fc + 0x18) == '\0') {
    even_ai_listening_visibility_set(1);
  }
  even_ai_hide_listening_text();
  if (pcVar3[9] == '\x01') {
    FUN_005537cc(0);
  }
  else {
    FUN_0055389a();
  }
  puVar13 = PTR_s_ID_EVEN_AI_COMMAND_EXECUTION_FAI_004e758c;
  puVar12 = PTR_s_ID_EVEN_AI_AI_SERVER_ERROR_004e7588;
  puVar11 = PTR_s_ID_EVEN_AI_ASR_SERVER_ERROR_004e7584;
  puVar10 = PTR_s_ID_EVEN_AI_AUDIO_ERROR_004e7580;
  puVar9 = PTR_s_ID_EVEN_AI_CURRENTLY_UNSUPPORTED_004e757c;
  puVar8 = PTR_s_ID_EVEN_AI_HAVING_TROUBLE_UNDERS_004e7578;
  puVar7 = PTR_s_ID_EVEN_AI_SERVER_ERROR_004e7574;
  puVar6 = PTR_s_ID_EVEN_AI_BLUETOOTH_DISCONNECTE_004e756c;
  puVar5 = PTR_s_ID_EVEN_AI_NETWORK_ERROR_004e7564;
  bVar2 = pcVar3[1];
  if (bVar2 == 1) {
    uVar16 = FUN_00460084(PTR_s_ID_EVEN_AI_NETWORK_ERROR_004e7564);
    uVar16 = FUN_0045fffe(puVar5,uVar16);
    even_ai_add_answer(uVar16,PTR_DAT_004e7568,0xff,1,1);
    goto LAB_004e7154;
  }
  if (bVar2 != 0) {
    if (bVar2 == 3) {
      uVar16 = FUN_00460084(PTR_s_ID_EVEN_AI_SERVER_ERROR_004e7574);
      uVar16 = FUN_0045fffe(puVar7,uVar16);
      even_ai_add_answer(uVar16,PTR_DAT_004e7568,0xff,1,1);
      goto LAB_004e7154;
    }
    if (bVar2 < 3) {
      uVar16 = FUN_00460084(PTR_s_ID_EVEN_AI_BLUETOOTH_DISCONNECTE_004e756c);
      uVar16 = FUN_0045fffe(puVar6,uVar16);
      even_ai_add_answer(uVar16,PTR_DAT_004e7570,0xff,1,1);
      goto LAB_004e7154;
    }
    if (bVar2 == 5) {
      uVar16 = FUN_00460084(PTR_s_ID_EVEN_AI_CURRENTLY_UNSUPPORTED_004e757c);
      uVar16 = FUN_0045fffe(puVar9,uVar16);
      even_ai_add_answer(uVar16,PTR_DAT_004e7568,0xff,1,1);
      goto LAB_004e7154;
    }
    if (bVar2 < 5) {
      uVar16 = FUN_00460084(PTR_s_ID_EVEN_AI_HAVING_TROUBLE_UNDERS_004e7578);
      uVar16 = FUN_0045fffe(puVar8,uVar16);
      even_ai_add_answer(uVar16,0,0xff,1,0);
      goto LAB_004e7154;
    }
    if (bVar2 == 7) {
      uVar16 = FUN_00460084(PTR_s_ID_EVEN_AI_ASR_SERVER_ERROR_004e7584);
      uVar16 = FUN_0045fffe(puVar11,uVar16);
      even_ai_add_answer(uVar16,PTR_DAT_004e7568,0xff,1,1);
      goto LAB_004e7154;
    }
    if (bVar2 < 7) {
      uVar16 = FUN_00460084(PTR_s_ID_EVEN_AI_AUDIO_ERROR_004e7580);
      uVar16 = FUN_0045fffe(puVar10,uVar16);
      even_ai_add_answer(uVar16,PTR_DAT_004e7568,0xff,1,1);
      goto LAB_004e7154;
    }
    if (bVar2 == 9) {
      uVar16 = FUN_00460084(PTR_s_ID_EVEN_AI_COMMAND_EXECUTION_FAI_004e758c);
      uVar16 = FUN_0045fffe(puVar13,uVar16);
      even_ai_add_answer(uVar16,PTR_DAT_004e7568,0xff,1,1);
      goto LAB_004e7154;
    }
    if (bVar2 < 9) {
      uVar16 = FUN_00460084(PTR_s_ID_EVEN_AI_AI_SERVER_ERROR_004e7588);
      uVar16 = FUN_0045fffe(puVar12,uVar16);
      even_ai_add_answer(uVar16,PTR_DAT_004e7568,0xff,1,1);
      goto LAB_004e7154;
    }
  }
  even_ai_add_answer(PTR_s_Unknown_Error_004e7590,PTR_DAT_004e7568,0xff,1,1);
LAB_004e7154:
  even_ai_layout_refresh();
  return;
}

