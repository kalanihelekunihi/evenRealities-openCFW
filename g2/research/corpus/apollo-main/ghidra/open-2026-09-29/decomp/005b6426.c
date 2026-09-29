
undefined8 conversate_ui_action_tag_update(undefined4 param_1,undefined4 param_2)

{
  char *pcVar1;
  uint uVar2;
  uint uVar3;
  undefined4 uVar4;
  undefined1 *puVar5;
  int iVar6;
  int iVar7;
  
  uVar2 = FUN_0059674e();
  uVar3 = FUN_005b0c18();
  pcVar1 = DAT_005b6958;
  if ((uVar2 == 0) || (uVar2 <= uVar3)) {
    uVar4 = 0xffffffff;
  }
  else {
    puVar5 = (undefined1 *)FUN_005964e2(0);
    if (puVar5 == (undefined1 *)0x0) {
      uVar4 = 0xffffffff;
    }
    else {
      uVar4 = func_0x005b0af6(*puVar5);
      iVar6 = FUN_005b1150(*(undefined4 *)(pcVar1 + 100),uVar4,*(undefined4 *)(puVar5 + 4));
      if (iVar6 == 0) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          param_2 = 0x126;
          FUN_0043d574(1,DAT_005b6950,DAT_005b694c,PTR_s_conversate_ui_action_tag_update_005b698c,
                       0x126,PTR_s_Failed_to_create_new_button_005b6988);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x4000000,PTR_s__conversate_ui_Failed_to_create_n_005b6990);
        }
        uVar4 = 0xffffffff;
      }
      else {
        FUN_0044daca(iVar6,0);
        if (pcVar1[0x8c] == '\0') {
          *(int *)(pcVar1 + 0x80) = iVar6;
          pcVar1[0x84] = '\0';
          pcVar1[0x85] = '\0';
          pcVar1[0x86] = '\0';
          pcVar1[0x87] = '\0';
          pcVar1[0x96] = '\0';
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            param_2 = 0x12f;
            FUN_0043d574(3,DAT_005b6950,DAT_005b694c,PTR_s_conversate_ui_action_tag_update_005b698c,
                         0x12f,PTR_s_AI_cue_display_is_disabled__set_c_005b6994);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0xc000000,PTR_s__conversate_ui_AI_cue_display_is_005b6998,
                                PTR_s__conversate_ui_AI_cue_display_is_005b6998);
          }
          uVar4 = 0;
        }
        else if (pcVar1[0x8e] == '\0') {
          if (pcVar1[0x96] == '\0') {
            FUN_005b0edc(1,0,PTR_s_tag_update_single_highlight_005b69a0);
            FUN_005b1072(iVar6,1);
            FUN_0058c622(iVar6,0xfa,0);
            FUN_0044ea2e(iVar6,0);
            *(int *)(pcVar1 + 0x80) = iVar6;
            pcVar1[0x84] = '\0';
            pcVar1[0x85] = '\0';
            pcVar1[0x86] = '\0';
            pcVar1[0x87] = '\0';
            pcVar1[0x96] = '\x01';
            FUN_005b13fe();
          }
          else if (pcVar1[0x97] == '\x01') {
            if (*(int *)(pcVar1 + 0x80) != 0) {
              FUN_005b1072(*(undefined4 *)(pcVar1 + 0x80),0);
              FUN_0058c6c4(*(undefined4 *)(pcVar1 + 0x80),0xfa,0);
            }
            FUN_005b1072(iVar6,1);
            FUN_0058c622(iVar6,0xfa,0);
            FUN_0044ea2e(iVar6,0);
            *(int *)(pcVar1 + 0x80) = iVar6;
            pcVar1[0x84] = '\0';
            pcVar1[0x85] = '\0';
            pcVar1[0x86] = '\0';
            pcVar1[0x87] = '\0';
            pcVar1[0x96] = '\x01';
          }
          else {
            conversate_tag_compute_animation_rect(pcVar1);
          }
          FUN_005b13fe();
          uVar4 = 0;
        }
        else {
          if (pcVar1[0x96] == '\x01') {
            conversate_tag_compute_animation_rect(pcVar1);
          }
          else {
            iVar7 = FUN_005967bc();
            if ((iVar7 == 1) && (*pcVar1 == '\x02')) {
              FUN_005b02e4(8,1);
            }
            *(int *)(pcVar1 + 0x80) = iVar6;
            pcVar1[0x84] = '\0';
            pcVar1[0x85] = '\0';
            pcVar1[0x86] = '\0';
            pcVar1[0x87] = '\0';
            FUN_005b0edc(0,0,PTR_s_tag_update_auto_pop_en_005b699c);
          }
          FUN_005b13fe();
          uVar4 = 0;
        }
      }
    }
  }
  return CONCAT44(param_2,uVar4);
}

