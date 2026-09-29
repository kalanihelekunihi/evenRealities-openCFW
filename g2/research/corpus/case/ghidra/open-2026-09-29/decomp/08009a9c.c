
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void glasses_sides_reset(int param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined1 auStack_28 [4];
  undefined4 local_24;
  
  iVar1 = _DAT_08009b34;
  if (param_1 != 0 || param_2 != 0) {
    if (*(char *)(_DAT_08009b34 + 4) == '\0') {
      *(undefined1 *)(_DAT_08009b34 + 4) = 1;
      case_copy_head8_to_tail8();
      iVar3 = case_or_words_88_8c(DAT_08009b64);
      if (iVar3 << 0x1a < 0) {
        case_reset_controller_context(DAT_08009b64);
      }
      FUN_080001b4(auStack_28,DAT_08009b68,0x14);
      uVar2 = DAT_08009b6c;
      FUN_08004d30(DAT_08009b6c,auStack_28);
      if (param_1 != 0) {
        left_indicator_sequence();
        case_emit_probe_train();
        case_write_profile_three();
        osDelay(10);
      }
      if (param_2 != 0) {
        right_indicator_sequence();
        case_emit_probe_train();
        case_write_profile_four();
        osDelay(10);
      }
      local_24 = 0;
      FUN_08004d30(uVar2,auStack_28);
      dual_side_indicator_update();
      *(undefined1 *)(iVar1 + 4) = 0;
    }
    else if (*(char *)(_DAT_08009b34 + 7) == '\0') {
      g2_log_printf(s_Cannot_reset_gls_since_2510_is_b_08009b37 + 1);
      g2_log_printf(&DAT_08009b60);
    }
  }
  return;
}

