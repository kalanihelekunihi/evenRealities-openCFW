
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_005e7ed4(undefined4 param_1,undefined4 param_2,undefined *param_3)

{
  undefined1 *puVar1;
  int iVar2;
  
  puVar1 = _DAT_005e8124;
  *_DAT_005e8124 = 1;
  iVar2 = osKernelGetTickCount();
  *(int *)(puVar1 + 4) = iVar2 + 60000;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0x32;
    param_3 = PTR_s_voice_timeout_start__due_in__d_m_005e8128;
    FUN_0043d574(3,PTR_s_terminal_timer_005e8134,PTR_s_D__01_workspace_s200_ap510b_iar__005e8130,
                 PTR_s_terminal_timer_voice_timeout_sta_005e812c,0x32,
                 PTR_s_voice_timeout_start__due_in__d_m_005e8128,60000);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__terminal_timer_voice_timeout_st_005e8138,
                        PTR_s__terminal_timer_voice_timeout_st_005e8138,60000);
  }
  return CONCAT44(param_3,param_2);
}

