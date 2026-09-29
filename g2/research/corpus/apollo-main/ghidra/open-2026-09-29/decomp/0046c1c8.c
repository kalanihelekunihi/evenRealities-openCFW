
longlong settings_set_brightness_level
                   (uint param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar1 = DAT_0046c6a8;
  if (param_1 < 0x65) {
    if (param_1 < 2) {
      param_1 = 2;
    }
  }
  else {
    param_1 = 100;
  }
  if (*(char *)(DAT_0046c6a8 + 2) != '\0') {
    uVar2 = service_time_current_epoch_get();
    *(undefined4 *)(iVar1 + 4) = uVar2;
    iVar3 = als_function_36(param_1 & 0xfffffffe);
    if (iVar3 == 0) {
      uVar2 = als_function_38();
      *(undefined4 *)(iVar1 + 0x24) = uVar2;
      *(undefined1 *)(iVar1 + 0x2c) = 1;
      FUN_00448e34();
    }
  }
  *(char *)(iVar1 + 1) = (char)(param_1 & 0xfffffffe);
  settings_apply_auto_brightness();
  return (ulonglong)param_4 << 0x20;
}

