
undefined8 FUN_0054c5b0(undefined4 param_1,undefined *param_2,uint param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  int *piVar2;
  char *pcVar3;
  undefined4 *puVar4;
  int iVar5;
  uint uVar6;
  undefined4 uStack_20;
  undefined *puStack_1c;
  uint uStack_18;
  undefined4 uStack_14;
  
  uStack_18 = param_3;
  uStack_14 = param_4;
  iVar5 = FUN_0043d0ce();
  uStack_20 = param_1;
  puStack_1c = param_2;
  if (iVar5 << 0x1e < 0) {
    puStack_1c = PTR_s_Navigation_rubber_band_animation_0054cf4c;
    uStack_20 = 0xbb5;
    FUN_0043d574(4,PTR_s_navigation_ui_0054cf58,DAT_0054cf54,
                 PTR_s_navigation_rubber_band_anim_comp_0054cf50);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__navigation_ui_Navigation_rubber_0054cf5c,
                        PTR_s__navigation_ui_Navigation_rubber_0054cf5c);
  }
  piVar2 = DAT_0054cca4;
  if ((*DAT_0054cca4 != 0) && (uVar6 = FUN_0043fce0(*DAT_0054cca4), uVar6 != 0)) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      puStack_1c = PTR_s_Navigation_content_container_Y_n_0054cf60;
      uStack_20 = 0xbbb;
      uStack_18 = uVar6;
      FUN_0043d574(2,PTR_s_navigation_ui_0054cf58,DAT_0054cf54,
                   PTR_s_navigation_rubber_band_anim_comp_0054cf50);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x8400000,PTR_s__navigation_ui_Navigation_conten_0054cf64,
                          PTR_s__navigation_ui_Navigation_conten_0054cf64,uVar6);
    }
    FUN_0043f142(*piVar2,0);
  }
  puVar1 = DAT_0054cca0;
  *DAT_0054cca0 = 0;
  puVar4 = DAT_0054ceb4;
  pcVar3 = DAT_0054ceb0;
  if (*DAT_0054ceb0 == '\x02') {
    iVar5 = ui_common_api_fn_00509dfa(*DAT_0054ceb4);
    if (iVar5 == 0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        puStack_1c = DAT_0054ceb8;
        uStack_20 = 0xbc4;
        FUN_0043d574(4,PTR_s_navigation_ui_0054cf58,DAT_0054cf54,
                     PTR_s_navigation_rubber_band_anim_comp_0054cf50);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054cf30,
                            PTR_s__navigation_ui_navigation_ui_ref_0054cf30);
      }
      ui_common_api_fn_00509e14(*puVar4,&uStack_18,1);
      if ((uStack_18 & 0xff) == 10) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          puStack_1c = PTR_s_navigation_ui_reflash_page_handl_0054cf34;
          uStack_20 = 0xbc9;
          FUN_0043d574(4,PTR_s_navigation_ui_0054cf58,DAT_0054cf54,
                       PTR_s_navigation_rubber_band_anim_comp_0054cf50);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054cf38,
                              PTR_s__navigation_ui_navigation_ui_ref_0054cf38);
        }
        FUN_0054cfd0(2);
        if (*DAT_0054d3b8 != 0) {
          FUN_0044d878(*DAT_0054d3b8);
        }
        *pcVar3 = '\t';
        *DAT_0054cccc = 0;
        *puVar1 = 0;
        ui_common_api_fn_00509f52(*puVar4);
        FUN_00548b98();
      }
      else if ((uStack_18 & 0xff) == 0x44) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          puStack_1c = PTR_s_navigation_ui_reflash_page_handl_0054cf3c;
          uStack_20 = 0xbd7;
          FUN_0043d574(4,PTR_s_navigation_ui_0054cf58,DAT_0054cf54,
                       PTR_s_navigation_rubber_band_anim_comp_0054cf50);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054cf40,
                              PTR_s__navigation_ui_navigation_ui_ref_0054cf40);
        }
        FUN_0054cfd0(1);
      }
      else if ((uStack_18 & 0xff) == 0x45) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          puStack_1c = PTR_s_navigation_ui_reflash_page_handl_0054cf44;
          uStack_20 = 0xbda;
          FUN_0043d574(4,PTR_s_navigation_ui_0054cf58,DAT_0054cf54,
                       PTR_s_navigation_rubber_band_anim_comp_0054cf50);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054cf48,
                              PTR_s__navigation_ui_navigation_ui_ref_0054cf48);
        }
        FUN_0054cfd0(0);
      }
    }
  }
  return CONCAT44(puStack_1c,uStack_20);
}

