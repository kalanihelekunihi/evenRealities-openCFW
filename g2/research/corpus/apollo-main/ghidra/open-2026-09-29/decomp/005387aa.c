
undefined8
_thread_notify_event_handler(int param_1,undefined *param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    iVar2 = 0xeb;
    param_2 = PTR_s_notifyValue___0x_x_00538bc0;
    param_3 = param_1;
    FUN_0043d574(4,DAT_00538b54,DAT_00538b50,PTR_s__thread_notify_event_handler_00538bc4,0xeb,
                 PTR_s_notifyValue___0x_x_00538bc0,param_1,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__task_ble_production_notifyValue_00538bc8,
                        PTR_s__task_ble_production_notifyValue_00538bc8,param_1,iVar2,param_2,
                        param_3);
  }
  if (param_1 << 9 < 0) {
    _thread_msg_handler();
  }
  if (param_1 << 8 < 0) {
    _thread_exit();
  }
  return CONCAT44(param_2,iVar2);
}

