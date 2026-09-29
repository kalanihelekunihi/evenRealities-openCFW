
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_005e7f6e(undefined4 param_1,undefined4 param_2,undefined *param_3)

{
  int iVar1;
  int iVar2;
  
  iVar2 = _DAT_005e8124;
  *(undefined1 *)(_DAT_005e8124 + 8) = 1;
  iVar1 = osKernelGetTickCount();
  *(int *)(iVar2 + 0xc) = iVar1 + 20000;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0x46;
    param_3 = PTR_s_asr_result_timeout_start__due_in_005e8148;
    FUN_0043d574(3,PTR_s_terminal_timer_005e8134,PTR_s_D__01_workspace_s200_ap510b_iar__005e8130,
                 PTR_s_terminal_timer_asr_result_timeou_005e814c,0x46,
                 PTR_s_asr_result_timeout_start__due_in_005e8148,20000);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__terminal_timer_asr_result_timeo_005e8150,
                        PTR_s__terminal_timer_asr_result_timeo_005e8150,20000);
  }
  return CONCAT44(param_3,param_2);
}

