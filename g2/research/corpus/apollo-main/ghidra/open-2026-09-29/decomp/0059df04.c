
undefined8
translate_ui_0059df04(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  iVar2 = FUN_0045a568();
  iVar1 = DAT_0059e26c;
  local_10 = param_3;
  local_c = param_4;
  if (iVar2 == 1) {
    if (*(int *)(DAT_0059e26c + 0x28) != 0) {
      iVar2 = osKernelGetTickCount();
      if (10000 < (uint)(iVar2 - *(int *)(iVar1 + 0x28))) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          local_c = DAT_0059e634;
          local_10 = 0x1cf;
          FUN_0043d574(2,DAT_0059e640,DAT_0059e63c,DAT_0059e638);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x8000000,PTR_s__translate_ui_Text_refresh_time_o_0059e644,
                              PTR_s__translate_ui_Text_refresh_time_o_0059e644);
        }
        FUN_0059ec28(2,1);
        *(undefined4 *)(iVar1 + 0x28) = 0;
      }
    }
  }
  return CONCAT44(local_c,local_10);
}

