
undefined4 ui_onboarding_main_sub_004A99D0(char *param_1,uint param_2)

{
  char cVar1;
  byte bVar2;
  int *piVar3;
  undefined4 uVar4;
  ushort uVar5;
  int iVar6;
  uint local_30;
  undefined4 local_2c;
  uint local_28;
  uint local_24 [3];
  undefined1 auStack_18 [8];
  
  piVar3 = DAT_004a9ddc;
  if (*DAT_004aa650 == 1) {
    ui_onboarding_main_sub_004A91F4(param_1);
  }
  else {
    cVar1 = *param_1;
    if (cVar1 == '\0') {
      if (*DAT_004aa03c == 0) {
        iVar6 = ui_onboarding_main_sub_004A979C(param_1,1,auStack_18);
        if (iVar6 == 0) {
          ui_onboarding_main_sub_004A97EA(auStack_18);
        }
      }
      else {
        ui_common_api_fn_00509ca2(*DAT_004aa210,param_1 + 1,7);
      }
    }
    else if (cVar1 == '\x01') {
      ui_onboarding_main_sub_004A93B0(param_1 + 1,param_2 - 1);
    }
    else if (cVar1 == '\x03') {
      FUN_0050a094();
    }
    else if (cVar1 == '\x04') {
      ui_onboarding_stock_sub_0050DB34(param_1 + 1,param_2 - 1);
    }
    else if (cVar1 == '\a') {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        local_24[0] = (uint)(byte)param_1[2];
        local_28 = (uint)(byte)param_1[1];
        local_2c = DAT_004aa214;
        local_30 = 0x764;
        FUN_0043d574(3,DAT_004a9c04,DAT_004a9c00,DAT_004aa218);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        local_30 = (uint)(byte)param_1[2];
        compress_log_output(0xc800000,DAT_004aa21c,DAT_004aa21c,param_1[1]);
      }
      FUN_0043c0e4(local_24,10,0);
      FUN_0043c0e4(local_24,10,0);
      uVar4 = DAT_004aa220;
      bVar2 = param_1[2];
      FUN_004b4728(local_24,DAT_004aa220,(byte)param_1[1] / 10,(uint)(byte)param_1[1] % 10);
      FUN_0049942e(*DAT_004aa224,local_24);
      FUN_0043c0e4(&local_30,10,0);
      FUN_0043c0e4(&local_30,10,0);
      FUN_004b4728(&local_30,uVar4,bVar2 / 10,(uint)bVar2 % 10);
      FUN_0049942e(*DAT_004aa228,&local_30);
    }
    else if (cVar1 == '\b') {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        local_2c = DAT_004a9d6c;
        local_30 = 0x772;
        FUN_0043d574(3,DAT_004a9c04,DAT_004a9c00,DAT_004aa218);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004a9dd8,DAT_004a9dd8);
      }
      ui_onboarding_main_sub_004A96DC(1);
    }
    else if (cVar1 == '\n') {
      if ((param_2 < 2) || (param_1[1] != '\x01')) {
        ui_onboarding_main_sub_004A9EDC();
      }
      else {
        ui_onboarding_main_sub_004AA16C();
      }
    }
    else if (cVar1 == '\v') {
      if ((1 < param_2) && (*DAT_004a9ddc != 0)) {
        bVar2 = param_1[1];
        uVar5 = FUN_0050ecee(*DAT_004a9ddc);
        if (bVar2 < uVar5) {
          FUN_0050ebe2(*piVar3,bVar2,1);
        }
      }
    }
    else if (cVar1 == '\f') {
      if (*(byte *)(DAT_004aa200 + 1) <= (byte)param_1[1]) {
        *(char *)(DAT_004aa200 + 1) = param_1[1];
        ui_onboarding_main_sub_004A9F84();
      }
    }
    else if (cVar1 == '\x11') {
      ui_onboarding_main_sub_004A96DC(0);
    }
  }
  return 0;
}

