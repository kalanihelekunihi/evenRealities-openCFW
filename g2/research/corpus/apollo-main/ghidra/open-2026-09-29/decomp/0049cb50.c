
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0049cb50(int param_1)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint auStack_1c [3];
  
  if (param_1 != 0) {
    uVar1 = FUN_0044104c(0xffffff);
    FUN_004412ec(param_1,uVar1,0);
    uVar1 = FUN_0049c08c(param_1,0);
    uVar2 = FUN_0044104c(_DAT_0049cdb8);
    iVar3 = FUN_0044102e(uVar1,uVar2);
    if (iVar3 != 0) {
      uVar1 = FUN_0044104c(0xffffff);
      FUN_0044140e(param_1,uVar1,0);
    }
    iVar3 = FUN_0043e2bc(param_1,PTR_PTR_0049cdd8);
    if ((iVar3 != 0) && (iVar3 = FUN_00498b50(param_1), iVar3 != 0)) {
      iVar3 = FUN_00488f6a(iVar3,auStack_1c);
      if (iVar3 == 1) {
        if (((((auStack_1c[0] & 0xffff) >> 8 == 7) || ((auStack_1c[0] & 0xffff) >> 8 == 8)) ||
            ((auStack_1c[0] & 0xffff) >> 8 == 9)) || ((auStack_1c[0] & 0xffff) >> 8 == 10)) {
          uVar1 = FUN_00441068(0xff,0xff,0xff);
          FUN_004413de(param_1,uVar1,0);
          FUN_004413fe(param_1,0xff,0);
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_dashboard_0049ce04,PTR_s_D__01_workspace_s200_ap510b_iar__0049ce00,
                         PTR_s_resume_widget_colors_recursive_0049cdfc,0x1c4,
                         PTR_s_Applied_white_recolor_to_indexed_0049cdf8,
                         (auStack_1c[0] & 0xffff) >> 8);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10400000,PTR_s__dashboard_Applied_white_recolor_0049ce08,
                                PTR_s__dashboard_Applied_white_recolor_0049ce08,
                                (auStack_1c[0] & 0xffff) >> 8);
          }
        }
        else if ((auStack_1c[0] & 0xffff) >> 8 == 6) {
          FUN_004413ce(param_1,0xff,0);
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_dashboard_0049ce04,PTR_s_D__01_workspace_s200_ap510b_iar__0049ce00,
                         PTR_s_resume_widget_colors_recursive_0049cdfc,0x1c8,
                         PTR_s_Restored_opacity_for_L8_image__c_0049ce0c,
                         (auStack_1c[0] & 0xffff) >> 8);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10400000,PTR_s__dashboard_Restored_opacity_for_L_0049ce10,
                                PTR_s__dashboard_Restored_opacity_for_L_0049ce10,
                                (auStack_1c[0] & 0xffff) >> 8);
          }
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_dashboard_0049ce04,PTR_s_D__01_workspace_s200_ap510b_iar__0049ce00,
                       PTR_s_resume_widget_colors_recursive_0049cdfc,0x1cd,
                       PTR_s_Failed_to_get_image_info__skippi_0049cdf0);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8000000,PTR_s__dashboard_Failed_to_get_image_i_0049cdf4,
                              PTR_s__dashboard_Failed_to_get_image_i_0049cdf4);
        }
      }
    }
    uVar4 = FUN_0044ddea(param_1);
    for (uVar5 = 0; uVar5 < uVar4; uVar5 = uVar5 + 1) {
      iVar3 = FUN_0044dce2(param_1,uVar5);
      if (iVar3 != 0) {
        FUN_0049cb50();
      }
    }
  }
  return;
}

