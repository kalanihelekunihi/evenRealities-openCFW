
void FUN_0054c844(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  undefined *puVar5;
  int iVar6;
  int local_138;
  undefined *local_134;
  int local_130;
  int local_12c;
  undefined *local_128;
  undefined *local_118;
  undefined4 local_108;
  undefined4 local_100;
  undefined4 local_fc;
  int local_d8;
  undefined *local_d4;
  undefined *local_c8;
  undefined *local_b8;
  undefined4 local_a8;
  undefined4 local_a0;
  undefined4 local_9c;
  int local_78;
  undefined *local_74;
  undefined *local_68;
  undefined *local_58;
  undefined4 local_48;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 uStack_18;
  
  piVar2 = DAT_0054ccb0;
  piVar1 = DAT_0054cca4;
  if (*DAT_0054ccb0 != 0) {
    uStack_18 = param_4;
    if (param_1 == '\0') {
      iVar3 = *(int *)s_8l7_pAp_0054cf88._0_4_;
      if (iVar3 < 5) {
        if (*DAT_0054cca4 != 0) {
          iVar3 = FUN_0043fce0(*DAT_0054cca4);
          if (iVar3 != 0) {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              local_134 = PTR_s_Navigation_content_container_Y_n_0054cf68;
              local_138 = 0xc15;
              local_130 = iVar3;
              FUN_0043d574(2,PTR_s_navigation_ui_0054cf58,DAT_0054cf54,
                           PTR_s_trigger_navigation_rubber_band_e_0054cf6c);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0x8400000,PTR_s__navigation_ui_Navigation_conten_0054cf70,
                                  PTR_s__navigation_ui_Navigation_conten_0054cf70,iVar3);
            }
            FUN_0043f142(*piVar1,0);
          }
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            local_12c = -0x10;
            local_130 = 0;
            local_134 = (undefined *)s_8l7_pAp_0054cf88._4_4_;
            local_138 = 0xc1d;
            FUN_0043d574(4,PTR_s_navigation_ui_0054cf58,DAT_0054cf54,
                         PTR_s_trigger_navigation_rubber_band_e_0054cf6c);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            local_138 = -0x10;
            compress_log_output(0x10800000,DAT_0054cf90,DAT_0054cf90,0);
          }
          FUN_004503d6(&local_d8);
          local_d8 = *piVar1;
          FUN_004506ce(&local_d8,0,0xfffffff0);
          local_a8 = 200;
          local_d4 = PTR_FUN_0054c83c_1_0054cf7c;
          local_b8 = PTR_LAB_00450672_1_0054cf80;
          local_9c = 200;
          local_a0 = 0;
          local_c8 = PTR_FUN_0054c5b0_1_0054cf84;
          *DAT_0054cca0 = 1;
          FUN_00450408(&local_d8);
        }
      }
      else {
        iVar4 = FUN_0044e4aa(*DAT_0054ccb0);
        puVar5 = (undefined *)((iVar3 + -5) * 0x28);
        if ((int)puVar5 < 0) {
          puVar5 = (undefined *)0x0;
        }
        iVar6 = iVar4 + 0x10;
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          local_134 = DAT_0054cf94;
          local_138 = 0xc34;
          local_130 = iVar4;
          local_12c = iVar6;
          local_128 = puVar5;
          FUN_0043d574(4,PTR_s_navigation_ui_0054cf58,DAT_0054cf54,
                       PTR_s_trigger_navigation_rubber_band_e_0054cf6c);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          local_138 = iVar6;
          local_134 = puVar5;
          compress_log_output(0x10c00000,DAT_0054cf98,DAT_0054cf98,iVar4);
        }
        FUN_004503d6(&local_138);
        local_138 = *piVar2;
        FUN_004506ce(&local_138,iVar4,iVar6);
        local_108 = 200;
        local_134 = (undefined *)DAT_0054cf9c;
        local_118 = PTR_LAB_00450672_1_0054cf80;
        local_fc = 200;
        local_100 = 0;
        local_128 = PTR_FUN_0054c5b0_1_0054cf84;
        *DAT_0054cca0 = 1;
        FUN_00450408(&local_138);
      }
    }
    else if (*DAT_0054cca4 != 0) {
      iVar3 = FUN_0043fce0(*DAT_0054cca4);
      if (iVar3 != 0) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          local_134 = PTR_s_Navigation_content_container_Y_n_0054cf68;
          local_138 = 0xbf3;
          local_130 = iVar3;
          FUN_0043d574(2,PTR_s_navigation_ui_0054cf58,DAT_0054cf54,
                       PTR_s_trigger_navigation_rubber_band_e_0054cf6c);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__navigation_ui_Navigation_conten_0054cf70,
                              PTR_s__navigation_ui_Navigation_conten_0054cf70,iVar3);
        }
        FUN_0043f142(*piVar1,0);
      }
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_12c = 0x10;
        local_130 = 0;
        local_134 = PTR_s_Navigation_rubber_band_TOP__norm_0054cf74;
        local_138 = 0xbfb;
        FUN_0043d574(4,PTR_s_navigation_ui_0054cf58,DAT_0054cf54,
                     PTR_s_trigger_navigation_rubber_band_e_0054cf6c);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        local_138 = 0x10;
        compress_log_output(0x10800000,PTR_s__navigation_ui_Navigation_rubber_0054cf78,
                            PTR_s__navigation_ui_Navigation_rubber_0054cf78,0);
      }
      FUN_004503d6(&local_78);
      local_78 = *piVar1;
      FUN_004506ce(&local_78,0,0x10);
      local_48 = 200;
      local_74 = PTR_FUN_0054c83c_1_0054cf7c;
      local_58 = PTR_LAB_00450672_1_0054cf80;
      local_3c = 200;
      local_40 = 0;
      local_68 = PTR_FUN_0054c5b0_1_0054cf84;
      *DAT_0054cca0 = 1;
      FUN_00450408(&local_78);
    }
  }
  return;
}

