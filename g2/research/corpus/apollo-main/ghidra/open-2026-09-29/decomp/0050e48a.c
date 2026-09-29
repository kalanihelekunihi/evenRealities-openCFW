
undefined8
ui_onboarding_stock_sub_0050E48A
          (int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x86a;
      param_3 = DAT_0050e91c;
      FUN_0043d574(1,DAT_0050e724,DAT_0050e720,DAT_0050e920,0x86a,DAT_0050e91c,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0050e924);
    }
  }
  else {
    iVar1 = ui_onboarding_stock_sub_0050E468(param_2);
    if (*(int *)(param_1 + 0x4c) != 0) {
      if (iVar1 < 2) {
        FUN_0043ded4(*(undefined4 *)(param_1 + 0x4c),1);
      }
      else {
        FUN_0043dfa4(*(undefined4 *)(param_1 + 0x4c),1);
      }
    }
    if (*(int *)(param_1 + 0x50) != 0) {
      if (iVar1 < 3) {
        FUN_0043ded4(*(undefined4 *)(param_1 + 0x50),1);
      }
      else {
        FUN_0043dfa4(*(undefined4 *)(param_1 + 0x50),1);
      }
    }
  }
  return CONCAT44(param_3,param_2);
}

