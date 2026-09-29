
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_00552948(undefined4 param_1,undefined4 param_2,undefined *param_3)

{
  undefined4 *puVar1;
  char cVar2;
  undefined4 uVar3;
  int iVar4;
  
  cVar2 = FUN_0045a568();
  puVar1 = _DAT_00552adc;
  if (cVar2 == '\x01') {
    uVar3 = osKernelGetTickCount();
    *puVar1 = uVar3;
    puVar1[1] = param_1;
    *(undefined1 *)(puVar1 + 2) = 1;
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      param_2 = 0x2a;
      param_3 = PTR_s_msg_notif_timer_mgr_start__timeo_00552b00;
      FUN_0043d574(4,PTR_s_message_notify_timer_00552aec,
                   PTR_s_D__01_workspace_s200_ap510b_iar__00552ae8,
                   PTR_s_msg_notif_timer_mgr_start_00552b04,0x2a,
                   PTR_s_msg_notif_timer_mgr_start__timeo_00552b00,param_1);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__message_notify_timer_msg_notif__00552b08,
                          PTR_s__message_notify_timer_msg_notif__00552b08,param_1);
    }
  }
  return CONCAT44(param_3,param_2);
}

