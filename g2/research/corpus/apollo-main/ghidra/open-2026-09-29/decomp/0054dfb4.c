
void FUN_0054dfb4(char param_1)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int local_d0;
  undefined *local_cc;
  int local_c8;
  int local_c4;
  undefined *local_c0;
  undefined *local_b0;
  undefined4 local_a0;
  undefined4 local_98;
  undefined4 local_94;
  int local_70;
  undefined *local_6c;
  undefined *local_60;
  undefined *local_50;
  undefined4 local_40;
  undefined4 local_38;
  undefined4 local_34;
  
  piVar2 = DAT_0054e618;
  piVar1 = DAT_0054e5e0;
  if (*DAT_0054e5e0 != 0) {
    if (param_1 == '\0') {
      iVar3 = FUN_0044e4aa(*DAT_0054e5e0);
      iVar5 = iVar3 + 0x10;
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_cc = PTR_s_Mode_rubber_band_BOTTOM__current_0054e648;
        local_d0 = 0xea1;
        local_c8 = iVar3;
        local_c4 = iVar5;
        FUN_0043d574(4,DAT_0054e448,DAT_0054e444,PTR_s_trigger_mode_rubber_band_effect_0054e62c);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        local_d0 = iVar5;
        compress_log_output(0x10800000,PTR_s__navigation_ui_Mode_rubber_band_B_0054e64c,
                            PTR_s__navigation_ui_Mode_rubber_band_B_0054e64c,iVar3);
      }
      FUN_004503d6(&local_d0);
      local_d0 = *piVar1;
      FUN_004506ce(&local_d0,iVar3,iVar5);
      local_a0 = 200;
      local_cc = PTR_FUN_0054daea_1_0054e650;
      local_b0 = PTR_LAB_00450672_1_0054e640;
      local_94 = 200;
      local_98 = 0;
      local_c0 = PTR_FUN_0054dd9c_1_0054e644;
      *DAT_0054e624 = 1;
      FUN_00450408(&local_d0);
    }
    else if (*DAT_0054e618 != 0) {
      iVar3 = FUN_0043fce0(*DAT_0054e618);
      if (iVar3 != 0) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          local_cc = PTR_s_Mode_content_container_Y_not_zer_0054e628;
          local_d0 = 0xe83;
          local_c8 = iVar3;
          FUN_0043d574(4,DAT_0054e448,DAT_0054e444,PTR_s_trigger_mode_rubber_band_effect_0054e62c);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__navigation_ui_Mode_content_cont_0054e630,
                              PTR_s__navigation_ui_Mode_content_cont_0054e630,iVar3);
        }
        FUN_0043f142(*piVar2,0);
      }
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_c4 = 0x10;
        local_c8 = 0;
        local_cc = PTR_s_Mode_rubber_band_TOP__normal_y___0054e634;
        local_d0 = 0xe8b;
        FUN_0043d574(4,DAT_0054e448,DAT_0054e444,PTR_s_trigger_mode_rubber_band_effect_0054e62c);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        local_d0 = 0x10;
        compress_log_output(0x10800000,PTR_s__navigation_ui_Mode_rubber_band_T_0054e638,
                            PTR_s__navigation_ui_Mode_rubber_band_T_0054e638,0);
      }
      FUN_004503d6(&local_70);
      local_70 = *piVar2;
      FUN_004506ce(&local_70,0,0x10);
      local_40 = 200;
      local_6c = PTR_FUN_0054c83c_1_0054e63c;
      local_50 = PTR_LAB_00450672_1_0054e640;
      local_34 = 200;
      local_38 = 0;
      local_60 = PTR_FUN_0054dd9c_1_0054e644;
      *DAT_0054e624 = 1;
      FUN_00450408(&local_70);
    }
  }
  return;
}

