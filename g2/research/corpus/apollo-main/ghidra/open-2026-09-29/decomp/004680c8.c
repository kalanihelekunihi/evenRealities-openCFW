
void onboarding_darken_widget_colors_recursive(int param_1)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  uint local_1c [3];
  
  if (param_1 != 0) {
    onboarding_get_style_bg_color(param_1,0);
    uVar4 = DAT_00468c30;
    uVar1 = FUN_0044104c(DAT_00468c30);
    FUN_004412ec(param_1,uVar1,0);
    uVar1 = onboarding_get_style_image_recolor(param_1,0);
    uVar2 = FUN_0044104c(0xffffff);
    iVar3 = FUN_0044102e(uVar1,uVar2);
    if (iVar3 != 0) {
      uVar4 = FUN_0044104c(uVar4);
      FUN_0044140e(param_1,uVar4,0);
    }
    iVar3 = FUN_0043e2bc(param_1,DAT_00468c34);
    if ((iVar3 != 0) && (iVar3 = FUN_00498b50(param_1), iVar3 != 0)) {
      iVar3 = FUN_00488f6a(iVar3,local_1c);
      if (iVar3 == 1) {
        if (((((local_1c[0] & 0xffff) >> 8 == 7) || ((local_1c[0] & 0xffff) >> 8 == 8)) ||
            ((local_1c[0] & 0xffff) >> 8 == 9)) || ((local_1c[0] & 0xffff) >> 8 == 10)) {
          uVar4 = FUN_00441068(0x33,0x33,0x33);
          FUN_004413de(param_1,uVar4,0);
          FUN_004413fe(param_1,0xff,0);
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,DAT_00468a3c,DAT_00468a38,DAT_00468c3c,0xa9,DAT_00468c38,
                         (local_1c[0] & 0xffff) >> 8);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_00468c40,DAT_00468c40,(local_1c[0] & 0xffff) >> 8);
          }
        }
        else if ((local_1c[0] & 0xffff) >> 8 == 6) {
          FUN_004413ce(param_1,0x20,0);
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,DAT_00468a3c,DAT_00468a38,DAT_00468c3c,0xad,DAT_00468c44,
                         (local_1c[0] & 0xffff) >> 8);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_00468c48,DAT_00468c48,(local_1c[0] & 0xffff) >> 8);
          }
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(2,DAT_00468a3c,DAT_00468a38,DAT_00468c3c,0xb2,DAT_00468c4c);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_00468c50,DAT_00468c50);
        }
      }
    }
    uVar5 = FUN_0044ddea(param_1);
    for (uVar6 = 0; uVar6 < uVar5; uVar6 = uVar6 + 1) {
      FUN_0044dce2(param_1,uVar6);
      onboarding_darken_widget_colors_recursive();
    }
  }
  return;
}

