
longlong SVC_Settings_SaveSettingConfigToKVCheck
                   (undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  undefined2 uVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = DAT_0046bee8;
  iVar3 = *(int *)(DAT_0046c694 + 4);
  uVar1 = FUN_0049acd4(DAT_0046bee8,0x18,0,param_4,param_2,param_3,param_4);
  *(undefined2 *)(iVar2 + 0x18) = uVar1;
  if (*(short *)(iVar3 + 0x18) == *(short *)(iVar2 + 0x18)) goto LAB_0046bee2;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0x155;
    FUN_0043d574(4,PTR_s_service_settings_0046c664,DAT_0046c660,DAT_0046c6a0,0x155,DAT_0046c69c);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_0046bed0:
    compress_log_output(0x10000000,DAT_0046c6a4);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_0046bed0;
  }
  FUN_00448e34();
LAB_0046bee2:
  return (ulonglong)param_2 << 0x20;
}

