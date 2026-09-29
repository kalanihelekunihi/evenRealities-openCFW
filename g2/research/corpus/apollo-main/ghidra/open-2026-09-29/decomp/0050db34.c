
undefined4
ui_onboarding_stock_sub_0050DB34(int param_1,uint param_2,uint param_3,undefined4 param_4)

{
  int *piVar1;
  uint *puVar2;
  int iVar3;
  undefined4 uVar4;
  int local_18;
  uint local_14;
  uint local_10;
  undefined4 uStack_c;
  
  puVar2 = DAT_0050dddc;
  local_18 = param_1;
  local_14 = param_2;
  local_10 = param_3;
  uStack_c = param_4;
  if (param_1 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_14 = DAT_0050e520;
      local_18 = 0x60a;
      FUN_0043d574(1,DAT_0050dc5c,DAT_0050dc58,DAT_0050e524);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0050e528,DAT_0050e528);
    }
    uVar4 = 0xffffffff;
  }
  else {
    if (*DAT_0050dddc < 6) {
      if (*(int *)(DAT_0050dc6c + *DAT_0050dddc * 8 + 4) != 0) {
        FUN_0044d878(*(undefined4 *)(DAT_0050dc6c + *DAT_0050dddc * 8 + 4));
      }
      ui_onboarding_stock_sub_0050DCBC(*puVar2);
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_10 = *puVar2;
        local_14 = DAT_0050e52c;
        local_18 = 0x61d;
        FUN_0043d574(2,DAT_0050dc5c,DAT_0050dc58,DAT_0050e524);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_0050e530,DAT_0050e530,*puVar2);
      }
    }
    piVar1 = DAT_0050dc68;
    if (((*DAT_0050dc64 == 1) && (*DAT_0050dc60 != 0)) && (*DAT_0050dc68 != 0)) {
      if (*DAT_0050e7e0 == 0) {
        FUN_0044d878(*DAT_0050dc68);
        ui_onboarding_stock_sub_0050D894(*piVar1);
      }
      else {
        local_18 = 0x47;
        local_14 = local_14 & 0xffffff00;
        ui_common_api_fn_00509ca2(*DAT_0050dc60,&local_18,5);
      }
    }
    uVar4 = 0;
  }
  return uVar4;
}

