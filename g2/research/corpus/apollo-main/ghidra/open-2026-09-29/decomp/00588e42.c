
undefined8 FUN_00588e42(undefined4 param_1,undefined4 param_2,undefined *param_3,undefined4 param_4)

{
  int iVar1;
  char *pcVar2;
  int iVar3;
  
  pcVar2 = DAT_00589384;
  iVar1 = DAT_00589354;
  if ((((*(char *)(DAT_00589350 + 0x20) == '\x02') && (*(char *)(DAT_00589354 + 4) == '\x02')) &&
      (*DAT_00589384 != '\x01')) &&
     ((*(int *)(DAT_00589354 + 0x1c) != 0 && (*DAT_0058936c == '\x01')))) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x5a;
      param_3 = PTR_s_Auto_scroll_timer_start_00589388;
      FUN_0043d574(3,DAT_00589364,DAT_00589360,PTR_s_teleprompt_timer_auto_scroll_sta_0058938c,0x5a,
                   PTR_s_Auto_scroll_timer_start_00589388,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__teleprompt_timer_Auto_scroll_ti_00589390,
                          PTR_s__teleprompt_timer_Auto_scroll_ti_00589390);
    }
    *pcVar2 = '\x01';
    iVar3 = osKernelGetTickCount();
    *DAT_00589394 = *(int *)(iVar1 + 0x1c) + iVar3;
  }
  return CONCAT44(param_3,param_2);
}

