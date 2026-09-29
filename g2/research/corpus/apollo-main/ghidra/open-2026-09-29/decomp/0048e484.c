
longlong android_notify_ancc_forward(undefined4 param_1,undefined4 param_2,undefined2 param_3)

{
  uint unaff_r7;
  
  service_ancc_notification_process(param_2,param_3);
  return (ulonglong)unaff_r7 << 0x20;
}

