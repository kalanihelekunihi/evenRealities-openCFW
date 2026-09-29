
undefined8 SVC_ANDROID_ParseNotification(int param_1,undefined *param_2)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = param_1;
  iVar2 = service_ancc_state_byte0_get();
  if (iVar2 != 0) {
    iVar2 = profileAnccGetActive();
    _androidParseNotification(param_1,iVar2);
    cVar1 = SVC_IsOnWhitelistByIdentifier(iVar2 + 8);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      iVar4 = 0x89;
      param_2 = PTR_s_Whitelist_check_result__appType__0048e8b8;
      FUN_0043d574(4,PTR_s_svc_android_notify_0048e85c,
                   PTR_s_D__01_workspace_s200_ap510b_iar__0048e858,
                   PTR_s_SVC_ANDROID_ParseNotification_0048e8bc,0x89,
                   PTR_s_Whitelist_check_result__appType__0048e8b8,cVar1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__svc_android_notify_Whitelist_ch_0048e8c0,
                          PTR_s__svc_android_notify_Whitelist_ch_0048e8c0,cVar1);
    }
    if ((cVar1 == '\x02') || (cVar1 == '\x03')) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        iVar4 = 0x8e;
        param_2 = PTR_s_Android_app__s__name__s__is_on_w_0048e8c4;
        FUN_0043d574(3,PTR_s_svc_android_notify_0048e85c,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0048e858,
                     PTR_s_SVC_ANDROID_ParseNotification_0048e8bc,0x8e,
                     PTR_s_Android_app__s__name__s__is_on_w_0048e8c4,iVar2 + 8,iVar2 + 0x48);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        iVar4 = iVar2 + 0x48;
        compress_log_output(0xc800000,PTR_s__svc_android_notify_Android_app__0048e8c8,
                            PTR_s__svc_android_notify_Android_app__0048e8c8,iVar2 + 8);
      }
      _androidSendCompleteNotificationMsg(iVar2,0x2fc);
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        iVar4 = 0x92;
        param_2 = PTR_s_Android_app__s__name__s__not_on_w_0048e8cc;
        FUN_0043d574(3,PTR_s_svc_android_notify_0048e85c,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0048e858,
                     PTR_s_SVC_ANDROID_ParseNotification_0048e8bc,0x92,
                     PTR_s_Android_app__s__name__s__not_on_w_0048e8cc,iVar2 + 8,iVar2 + 0x48);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        iVar4 = iVar2 + 0x48;
        compress_log_output(0xc800000,PTR_s__svc_android_notify_Android_app__0048e8d0,
                            PTR_s__svc_android_notify_Android_app__0048e8d0,iVar2 + 8);
      }
    }
  }
  return CONCAT44(param_2,iVar4);
}

