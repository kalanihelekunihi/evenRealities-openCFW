
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_005529e4(undefined4 param_1,undefined4 param_2)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  
  piVar1 = _DAT_00552adc;
  if ((char)_DAT_00552adc[2] == '\x01') {
    iVar3 = osKernelGetTickCount();
    uVar4 = iVar3 - *piVar1;
    if (uVar4 < (uint)piVar1[1]) {
      uVar2 = 0;
    }
    else {
      *(undefined1 *)(piVar1 + 2) = 2;
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_2 = 0x3e;
        FUN_0043d574(4,PTR_s_message_notify_timer_00552aec,
                     PTR_s_D__01_workspace_s200_ap510b_iar__00552ae8,
                     PTR_s_msg_notif_timer_mgr_check_timeou_00552b1c,0x3e,
                     PTR_s_msg_notif_timer_mgr_check_timeou_00552b18,uVar4);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__message_notify_timer_msg_notif__00552b20,
                            PTR_s__message_notify_timer_msg_notif__00552b20,uVar4);
      }
      uVar2 = 1;
    }
  }
  else {
    uVar2 = 0;
  }
  return CONCAT44(param_2,uVar2);
}

