
undefined4
ui_onboarding_stock_sub_0050D894
          (int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int *piVar2;
  undefined2 uVar3;
  int iVar4;
  int iVar5;
  
  piVar1 = DAT_0050dc60;
  if (param_1 == 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0050dc5c,DAT_0050dc58,DAT_0050dcac,0x522,DAT_0050dca8,param_3,param_4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0050dcb0,DAT_0050dcb0);
    }
    return 0xffffffff;
  }
  if (*DAT_0050dc60 != 0) {
    ui_common_api_fn_00509c96(*DAT_0050dc60);
    *piVar1 = 0;
  }
  iVar4 = ui_common_api_fn_00509c1c();
  *piVar1 = iVar4;
  piVar2 = DAT_0050e450;
  if (*piVar1 != 0) {
    iVar4 = FUN_0043de82(param_1);
    *piVar2 = iVar4;
    iVar4 = DAT_0050db2c;
    if (*piVar2 != 0) {
      *(int *)(DAT_0050db2c + 0x128) = *piVar2;
      FUN_0043f09a(*piVar2,0x14,0x11);
      FUN_0043f4c0(*piVar2,0x21b,0xfe);
      FUN_0044129e(*piVar2,0,0);
      FUN_0044129e(*piVar2,0,0);
      FUN_0044131c(*piVar2,0,0);
      ui_onboarding_stock_sub_0050CA24(*piVar2,0,0);
      FUN_0044e368(*piVar2,0);
      iVar5 = DAT_0050dc50 * *DAT_0050dc54;
      ui_onboarding_stock_sub_0050CB30(iVar4,*piVar2,iVar5,0);
      ui_onboarding_stock_sub_0050CB30(iVar4 + 0x60,*piVar2,iVar5 + 0x120,1);
      ui_onboarding_stock_sub_0050CB30(iVar4 + 0xc0,*piVar2,iVar5 + 0x240,2);
      *(undefined1 *)(iVar4 + 0x124) = 0;
      ui_onboarding_stock_sub_0050D532();
      ui_onboarding_stock_sub_0050D35A(iVar4,0);
      *DAT_0050dc64 = 1;
      ui_onboarding_stock_sub_0050E7F0();
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        uVar3 = ui_onboarding_stock_sub_0050CB28();
        FUN_0043d574(3,DAT_0050dc5c,DAT_0050dc58,DAT_0050dcac,0x579,DAT_0050e460,uVar3);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        uVar3 = ui_onboarding_stock_sub_0050CB28();
        compress_log_output(0xc400000,DAT_0050e518,DAT_0050e518,uVar3);
      }
      return 0;
    }
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0050dc5c,DAT_0050dc58,DAT_0050dcac,0x534,DAT_0050e454);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0050e458,DAT_0050e458);
    }
    return 0xffffffff;
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(1,DAT_0050dc5c,DAT_0050dc58,DAT_0050dcac,0x52d,DAT_0050dcb4);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x4000000,DAT_0050dcb8);
  }
  return 0xffffffff;
}

