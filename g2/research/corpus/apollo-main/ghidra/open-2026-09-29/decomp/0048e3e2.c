
undefined8
Thread_SendEvtToNotifTask
          (undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar2 = 0xf8;
    param_2 = PTR_s_Thread_SendEvtToNotifTask___0x_x_0048e478;
    param_3 = param_1;
    FUN_0043d574(4,PTR_s_task_notif_0048e43c,PTR_s_D__01_workspace_s200_ap510b_iar__0048e438,
                 PTR_s_Thread_SendEvtToNotifTask_0048e47c,0xf8,
                 PTR_s_Thread_SendEvtToNotifTask___0x_x_0048e478,param_1,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__task_notif_Thread_SendEvtToNoti_0048e480,
                        PTR_s__task_notif_Thread_SendEvtToNoti_0048e480,param_1,uVar2,param_2,
                        param_3);
  }
  osThreadFlagsSet(*(undefined4 *)(DAT_0048e444 + 8),param_1);
  return CONCAT44(param_2,uVar2);
}

