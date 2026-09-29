
undefined4 FUN_004e1b30(int param_1,char *param_2,uint param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iStack_20;
  char *pcStack_1c;
  uint uStack_18;
  undefined4 uStack_14;
  
  iStack_20 = param_1;
  pcStack_1c = param_2;
  uStack_18 = param_3;
  uStack_14 = param_4;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    pcStack_1c = PTR_s_MessageNotify_recv_data_len____d_004e1f30;
    iStack_20 = 0x4c;
    uStack_18 = param_3;
    FUN_0043d574(4,PTR_s_message_notify_page_004e1f3c,
                 PTR_s_D__01_workspace_s200_ap510b_iar__004e1f38,
                 PTR_s_MessageNotify_common_data_handle_004e1f34);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__message_notify_page_MessageNoti_004e1f40,
                        PTR_s__message_notify_page_MessageNoti_004e1f40,param_3);
  }
  if (param_1 == 0) {
    APP_PbRxNotificationFrameDataProcess(param_2,param_3 & 0xffff);
  }
  else if ((param_1 == 5) && (*param_2 == '\x01')) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uStack_18 = (uint)(byte)param_2[1];
      pcStack_1c = PTR_s_recv_msg_notif_startup__d_004e1f44;
      iStack_20 = 0x5c;
      FUN_0043d574(3,PTR_s_message_notify_page_004e1f3c,
                   PTR_s_D__01_workspace_s200_ap510b_iar__004e1f38,
                   PTR_s_MessageNotify_common_data_handle_004e1f34);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__message_notify_page_recv_msg_no_004e1f48,
                          PTR_s__message_notify_page_recv_msg_no_004e1f48,param_2[1]);
    }
    if ((param_2[1] == '\x02') || (param_2[1] == '\x04')) {
      FUN_004e1b28(2);
      uVar1 = *(undefined4 *)(param_2 + 2);
      FUN_0043c0e4(&iStack_20,6,0);
      iStack_20 = CONCAT22(iStack_20._2_2_,0x301);
      FUN_0045a8ee(4,&iStack_20,6,uVar1);
    }
  }
  return 0;
}

