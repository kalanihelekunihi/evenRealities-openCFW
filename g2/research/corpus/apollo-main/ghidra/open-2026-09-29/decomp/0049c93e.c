
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0049c93e(int param_1)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  uint auStack_1c [3];
  
  if (param_1 != 0) {
    FUN_0049c07e(param_1,0);
    uVar4 = _DAT_0049cdb8;
    uVar1 = FUN_0044104c(_DAT_0049cdb8);
    FUN_004412ec(param_1,uVar1,0);
    uVar1 = FUN_0049c08c(param_1,0);
    uVar2 = FUN_0044104c(0xffffff);
    iVar3 = FUN_0044102e(uVar1,uVar2);
    if (iVar3 != 0) {
      uVar4 = FUN_0044104c(uVar4);
      FUN_0044140e(param_1,uVar4,0);
    }
    iVar3 = FUN_0043e2bc(param_1,PTR_PTR_0049cdd8);
    if ((iVar3 != 0) && (iVar3 = FUN_00498b50(param_1), iVar3 != 0)) {
      iVar3 = FUN_00488f6a(iVar3,auStack_1c);
      if (iVar3 == 1) {
        if (((((auStack_1c[0] & 0xffff) >> 8 == 7) || ((auStack_1c[0] & 0xffff) >> 8 == 8)) ||
            ((auStack_1c[0] & 0xffff) >> 8 == 9)) || ((auStack_1c[0] & 0xffff) >> 8 == 10)) {
          uVar4 = FUN_00441068(0x33,0x33,0x33);
          FUN_004413de(param_1,uVar4,0);
          FUN_004413fe(param_1,0xff,0);
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_dashboard_0049cb30,DAT_0049cb2c,
                         PTR_s_darken_widget_colors_recursive_0049cde0,0x18d,
                         PTR_s_Applied_recolor_to_indexed_image_0049cddc,
                         (auStack_1c[0] & 0xffff) >> 8);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10400000,PTR_s__dashboard_Applied_recolor_to_in_0049cde4,
                                PTR_s__dashboard_Applied_recolor_to_in_0049cde4,
                                (auStack_1c[0] & 0xffff) >> 8);
          }
        }
        else if ((auStack_1c[0] & 0xffff) >> 8 == 6) {
          FUN_004413ce(param_1,0x40,0);
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_dashboard_0049cb30,DAT_0049cb2c,
                         PTR_s_darken_widget_colors_recursive_0049cde0,0x191,
                         PTR_s_Applied_opacity_to_L8_image__cf__0049cde8,
                         (auStack_1c[0] & 0xffff) >> 8);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10400000,PTR_s__dashboard_Applied_opacity_to_L8_0049cdec,
                                PTR_s__dashboard_Applied_opacity_to_L8_0049cdec,
                                (auStack_1c[0] & 0xffff) >> 8);
          }
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_dashboard_0049cb30,DAT_0049cb2c,
                       PTR_s_darken_widget_colors_recursive_0049cde0,0x196,
                       PTR_s_Failed_to_get_image_info__skippi_0049cdf0);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8000000,PTR_s__dashboard_Failed_to_get_image_i_0049cdf4,
                              PTR_s__dashboard_Failed_to_get_image_i_0049cdf4);
        }
      }
    }
    uVar5 = FUN_0044ddea(param_1);
    for (uVar6 = 0; uVar6 < uVar5; uVar6 = uVar6 + 1) {
      iVar3 = FUN_0044dce2(param_1,uVar6);
      if (iVar3 != 0) {
        FUN_0049c93e();
      }
    }
  }
  return;
}

