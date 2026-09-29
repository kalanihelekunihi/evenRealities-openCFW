
uint ui_onboarding_main_sub_004A91F4
               (byte *param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int *piVar2;
  ushort uVar3;
  int iVar4;
  uint uVar5;
  
  piVar2 = DAT_004a9ddc;
  if ((param_2 == 0) || (param_1 == (byte *)0x0)) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004a9c04,DAT_004a9c00,DAT_004a9bfc,0x537,DAT_004a9bf8,param_2,param_1,
                   param_4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_004a9c08,DAT_004a9c08,param_2,param_1);
    }
    uVar5 = 0;
  }
  else if (*param_1 == 0) {
    uVar5 = *DAT_004a99c8;
    if (uVar5 == 0) {
      uVar5 = FUN_0050aafc(param_1,param_2);
    }
    else if (uVar5 == 1) {
      uVar5 = ui_onboarding_stock_sub_0050D578(param_1,param_2);
    }
  }
  else {
    uVar5 = (uint)*param_1;
    if (uVar5 == 1) {
      uVar5 = ui_onboarding_main_sub_004A93B0(param_1 + 1,param_2 - 1);
    }
    else if (uVar5 == 3) {
      uVar5 = 0;
      if (*DAT_004a99c8 != 0) {
        uVar5 = FUN_0050a094();
      }
    }
    else if (uVar5 == 4) {
      uVar5 = ui_onboarding_stock_sub_0050DB34(param_1 + 1,param_2 - 1);
    }
    else if (uVar5 == 8) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(3,DAT_004a9c04,DAT_004a9c00,DAT_004a9bfc,0x56d,DAT_004a9d6c);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004a9dd8,DAT_004a9dd8);
      }
      uVar5 = ui_onboarding_main_sub_004A96DC(1);
    }
    else if (uVar5 == 10) {
      if ((param_2 < 2) || (param_1[1] != 1)) {
        uVar5 = ui_onboarding_main_sub_004A9EDC();
      }
      else {
        uVar5 = ui_onboarding_main_sub_004AA16C();
      }
    }
    else if (uVar5 == 0xb) {
      if ((1 < param_2) && (uVar5 = 0, *DAT_004a9ddc != 0)) {
        bVar1 = param_1[1];
        uVar3 = FUN_0050ecee(*DAT_004a9ddc);
        uVar5 = (uint)uVar3;
        if (bVar1 < uVar5) {
          uVar5 = FUN_0050ebe2(*piVar2,bVar1,1);
        }
      }
    }
    else if (uVar5 == 0xc) {
      bVar1 = param_1[1];
      uVar5 = (uint)bVar1;
      if (*(byte *)(DAT_004a9f68 + 1) <= bVar1) {
        *(byte *)(DAT_004a9f68 + 1) = bVar1;
        uVar5 = ui_onboarding_main_sub_004A9F84();
      }
    }
    else if (uVar5 == 0x11) {
      uVar5 = ui_onboarding_main_sub_004A96DC(0);
    }
  }
  return uVar5;
}

