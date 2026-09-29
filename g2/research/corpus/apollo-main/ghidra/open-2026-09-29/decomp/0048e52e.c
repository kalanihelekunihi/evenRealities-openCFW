
undefined8
_androidSendCompleteNotificationMsg
          (undefined4 param_1,uint param_2,undefined *param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = param_2;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar2 = 0x31;
    param_3 = PTR_s_android_Send_Complete_Notificati_0048e86c;
    FUN_0043d574(4,PTR_s_svc_android_notify_0048e85c,PTR_s_D__01_workspace_s200_ap510b_iar__0048e858
                 ,PTR_s__androidSendCompleteNotification_0048e870,0x31,
                 PTR_s_android_Send_Complete_Notificati_0048e86c,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__svc_android_notify_android_Send_0048e874);
  }
  FUN_00464d1c(0x101,param_1,param_2 & 0xffff,PTR__rxSyncEventCallback_1_0048e878);
  return CONCAT44(param_3,uVar2);
}

