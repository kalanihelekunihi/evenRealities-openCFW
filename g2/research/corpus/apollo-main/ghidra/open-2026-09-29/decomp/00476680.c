
void fw_event_loop_task(void)

{
  int iVar1;
  int iVar2;
  undefined4 in_r3;
  undefined4 uStack_14;
  code *pcStack_10;
  undefined4 uStack_c;
  
  uStack_c = in_r3;
  do {
    while (iVar1 = osMessageQueueGet(*DAT_00476bf0,&uStack_14,0,0xffffffff), iVar1 == 0) {
      (*pcStack_10)(uStack_14);
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00476c04,DAT_00476c00,PTR_s_fw_evt_loop_task_00476c40,0x8c,
                   PTR_s__fw_evt_loop_task_app_treat_even_00476c3c,iVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__evtloop__fw_evt_loop_task_app_t_00476c44,
                          PTR_s__evtloop__fw_evt_loop_task_app_t_00476c44,iVar1);
    }
  } while( true );
}

