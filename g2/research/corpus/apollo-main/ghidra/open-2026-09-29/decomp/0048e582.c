
void _androidParseNotification(undefined4 param_1,undefined4 *param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  
  iVar1 = cJSON_Parse();
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_svc_android_notify_0048e85c,
                   PTR_s_D__01_workspace_s200_ap510b_iar__0048e858,
                   PTR_s__androidParseNotification_0048e880,0x39,
                   PTR_s_error_root_JSON_NODE__0048e87c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__svc_android_notify_error_root_J_0048e884);
    }
  }
  else {
    iVar2 = cJSON_GetObjectItem(iVar1,PTR_s_android_notification_0048e888);
    if (iVar2 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_svc_android_notify_0048e85c,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0048e858,
                     PTR_s__androidParseNotification_0048e880,0x3f,
                     PTR_s_NOT_FOUND_Android_msg_JSON_NODE__0048e88c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__svc_android_notify_NOT_FOUND_An_0048e890,
                            PTR_s__svc_android_notify_NOT_FOUND_An_0048e890);
      }
      cJSON_Delete(iVar1);
    }
    else {
      iVar3 = cJSON_GetObjectItem(iVar2,PTR_s_app_identifier_0048e894);
      iVar4 = cJSON_GetObjectItem(iVar2,PTR_s_msg_id_0048e898);
      iVar5 = cJSON_GetObjectItem(iVar2,PTR_s_action_0048e89c);
      iVar6 = cJSON_GetObjectItem(iVar2,PTR_DAT_0048e8a0);
      iVar7 = cJSON_GetObjectItem(iVar2,PTR_s_title_0048e8a4);
      iVar8 = cJSON_GetObjectItem(iVar2,PTR_s_subtitle_0048e8a8);
      iVar9 = cJSON_GetObjectItem(iVar2,PTR_s_message_0048e8ac);
      iVar10 = cJSON_GetObjectItem(iVar2,PTR_DAT_0048e8b0);
      iVar2 = cJSON_GetObjectItem(iVar2,PTR_s_display_name_0048e8b4);
      FUN_0043c0e4(param_2,0x2fc,0);
      if (iVar4 != 0) {
        *param_2 = *(undefined4 *)(iVar4 + 0x14);
      }
      if (iVar5 != 0) {
        *(char *)(param_2 + 0xbe) = (char)*(undefined4 *)(iVar5 + 0x14);
      }
      if (iVar6 != 0) {
        *(char *)(param_2 + 1) = (char)*(undefined4 *)(iVar6 + 0x14);
      }
      if (iVar3 != 0) {
        FUN_0044b5a0(param_2 + 2,*(undefined4 *)(iVar3 + 0x10),0x3f);
      }
      if (iVar7 != 0) {
        FUN_0044b5a0(param_2 + 0x1a,*(undefined4 *)(iVar7 + 0x10),0x3f);
      }
      if (iVar9 != 0) {
        FUN_0044b5a0(param_2 + 0x3a,*(undefined4 *)(iVar9 + 0x10),0x1ff);
      }
      if (iVar8 != 0) {
        FUN_0044b5a0(param_2 + 0x2a,*(undefined4 *)(iVar8 + 0x10),0x3f);
      }
      if (iVar10 != 0) {
        FUN_0044b5a0(param_2 + 0xba,*(undefined4 *)(iVar10 + 0x10),0xf);
      }
      if (iVar2 != 0) {
        FUN_0044b5a0(param_2 + 0x12,*(undefined4 *)(iVar2 + 0x10),0x1f);
      }
      cJSON_Delete(iVar1);
    }
  }
  return;
}

