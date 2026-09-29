
undefined8 FUN_005967bc(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r5;
  
  if (*(char *)(DAT_00596abc + 0x8c) == '\0') {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x17d;
      FUN_0043d574(4,DAT_00596a8c,DAT_00596a88,PTR_s_conversate_tag_auto_pop_check_00596ac4,0x17d,
                   PTR_s_AI_cue_display_is_disabled_00596ac0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__conversate_tag_AI_cue_display_i_00596ac8,
                          PTR_s__conversate_tag_AI_cue_display_i_00596ac8);
    }
    uVar2 = 0;
  }
  else if (*(char *)(DAT_00596abc + 0x8e) == '\0') {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x182;
      FUN_0043d574(4,DAT_00596a8c,DAT_00596a88,PTR_s_conversate_tag_auto_pop_check_00596ac4,0x182,
                   PTR_s_Auto_pop_is_disabled_00596acc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__conversate_tag_Auto_pop_is_disa_00596ad0,
                          PTR_s__conversate_tag_Auto_pop_is_disa_00596ad0);
    }
    uVar2 = 0;
  }
  else if (*(char *)((int)DAT_00596998 + 10) == '\0') {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x187;
      FUN_0043d574(2,DAT_00596a8c,DAT_00596a88,PTR_s_conversate_tag_auto_pop_check_00596ac4,0x187,
                   DAT_00596a68);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__conversate_tag_Storage_not_init_00596a6c,
                          PTR_s__conversate_tag_Storage_not_init_00596a6c);
    }
    uVar2 = 0;
  }
  else if (*DAT_00596998 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x18c;
      FUN_0043d574(2,DAT_00596a8c,DAT_00596a88,PTR_s_conversate_tag_auto_pop_check_00596ac4,0x18c,
                   PTR_s_Head_is_NULL__no_previous_node_00596ad4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__conversate_tag_Head_is_NULL__no_00596ad8,
                          PTR_s__conversate_tag_Head_is_NULL__no_00596ad8);
    }
    uVar2 = 0;
  }
  else if (DAT_00596998[1] == *DAT_00596998) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x191;
      FUN_0043d574(4,DAT_00596a8c,DAT_00596a88,PTR_s_conversate_tag_auto_pop_check_00596ac4,0x191,
                   PTR_s_Auto_disp_node_is_head__no_need_t_00596adc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__conversate_tag_Auto_disp_node_i_00596ae0,
                          PTR_s__conversate_tag_Auto_disp_node_i_00596ae0);
    }
    uVar2 = 0;
  }
  else {
    uVar2 = 1;
  }
  return CONCAT44(unaff_r5,uVar2);
}

