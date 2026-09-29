
undefined4
SVC_Settings_BrightnessLevelToLumAndCurrent
          (uint param_1,uint *param_2,int *param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  
  if (param_1 < 0x65) {
    if (param_1 < 2) {
      param_1 = 2;
    }
  }
  else {
    param_1 = 100;
  }
  iVar1 = SVC_Settings_GetMaxLum();
  if (param_1 < 0x1f) {
    *param_2 = 0;
    iVar3 = ((param_1 - 2) * (iVar1 + -0x14d) + 0xe) / 0x1c + 0x14d;
    *param_3 = iVar3;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_service_settings_0046c664,DAT_0046c660,DAT_0046c708,0x223,DAT_0046c704,
                   param_1,iVar3,iVar1,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xcc00000,DAT_0046c70c,DAT_0046c70c,param_1,iVar3,iVar1);
    }
  }
  else {
    uVar4 = (param_1 * 0x24 - 0x415) / 0x46;
    *param_2 = uVar4;
    *param_3 = iVar1;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_service_settings_0046c664,DAT_0046c660,DAT_0046c708,0x22d,DAT_0046c710,
                   param_1,uVar4,iVar1,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xcc00000,PTR_s__service_settings_Convert_bright_0046c714,
                          PTR_s__service_settings_Convert_bright_0046c714,param_1,uVar4,iVar1);
    }
  }
  return 0;
}

