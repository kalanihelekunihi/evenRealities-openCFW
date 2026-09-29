
undefined8 FUN_0054dd9c(undefined4 param_1,undefined4 param_2,undefined *param_3,uint param_4)

{
  undefined4 *puVar1;
  int *piVar2;
  int iVar3;
  uint uVar4;
  undefined4 uStack_18;
  undefined *puStack_14;
  uint uStack_10;
  
  uStack_10 = param_4;
  iVar3 = FUN_0043d0ce();
  uStack_18 = param_2;
  puStack_14 = param_3;
  if (iVar3 << 0x1e < 0) {
    puStack_14 = PTR_s_Mode_rubber_band_animation_compl_0054e60c;
    uStack_18 = 0xe58;
    FUN_0043d574(4,DAT_0054e448,DAT_0054e444,PTR_s_mode_rubber_band_anim_complete_c_0054e610);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__navigation_ui_Mode_rubber_band_a_0054e614,
                        PTR_s__navigation_ui_Mode_rubber_band_a_0054e614);
  }
  piVar2 = DAT_0054e618;
  if ((*DAT_0054e618 != 0) && (uVar4 = FUN_0043fce0(*DAT_0054e618), uVar4 != 0)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      puStack_14 = DAT_0054e61c;
      uStack_18 = 0xe5e;
      uStack_10 = uVar4;
      FUN_0043d574(4,DAT_0054e448,DAT_0054e444,PTR_s_mode_rubber_band_anim_complete_c_0054e610);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0054e620,DAT_0054e620,uVar4);
    }
    FUN_0043f142(*piVar2,0);
  }
  *DAT_0054e624 = 0;
  puVar1 = DAT_0054e5e4;
  iVar3 = ui_common_api_fn_00509dfa(*DAT_0054e5e4);
  if (iVar3 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      puStack_14 = PTR_s_Mode_select_page__receive_event_f_0054e5e8;
      uStack_18 = 0xe67;
      FUN_0043d574(4,DAT_0054e448,DAT_0054e444,PTR_s_mode_rubber_band_anim_complete_c_0054e610);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__navigation_ui_Mode_select_page__0054e5f0,
                          PTR_s__navigation_ui_Mode_select_page__0054e5f0);
    }
    ui_common_api_fn_00509e14(*puVar1,&uStack_10,1);
    if ((uStack_10 & 0xff) == 10) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        puStack_14 = PTR_s_Mode_select_page__receive_clicke_0054e5f4;
        uStack_18 = 0xe6c;
        FUN_0043d574(4,DAT_0054e448,DAT_0054e444,PTR_s_mode_rubber_band_anim_complete_c_0054e610);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__navigation_ui_Mode_select_page__0054e5f8,
                            PTR_s__navigation_ui_Mode_select_page__0054e5f8);
      }
      FUN_0054e1a8(2);
    }
    else if ((uStack_10 & 0xff) == 0x44) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        puStack_14 = PTR_s_Mode_select_page__receive_scroll_0054e5fc;
        uStack_18 = 0xe6f;
        FUN_0043d574(4,DAT_0054e448,DAT_0054e444,PTR_s_mode_rubber_band_anim_complete_c_0054e610);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__navigation_ui_Mode_select_page__0054e600,
                            PTR_s__navigation_ui_Mode_select_page__0054e600);
      }
      FUN_0054e1a8(1);
    }
    else if ((uStack_10 & 0xff) == 0x45) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        puStack_14 = PTR_s_Mode_select_page__receive_scroll_0054e604;
        uStack_18 = 0xe72;
        FUN_0043d574(4,DAT_0054e448,DAT_0054e444,PTR_s_mode_rubber_band_anim_complete_c_0054e610);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__navigation_ui_Mode_select_page__0054e608,
                            PTR_s__navigation_ui_Mode_select_page__0054e608);
      }
      FUN_0054e1a8(0);
    }
  }
  return CONCAT44(puStack_14,uStack_18);
}

