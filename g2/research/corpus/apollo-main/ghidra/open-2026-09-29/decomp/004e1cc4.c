
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_004e1cc4(char *param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  uint uVar3;
  
  if ((param_1 == (char *)0x0) || (param_2 == 0)) {
    FUN_00551ed8(*_DAT_004e1f4c,0);
    uVar3 = param_2;
  }
  else {
    uVar3 = param_2;
    if (*param_1 == '\x03') {
      cVar1 = param_1[1];
      if (*_DAT_004e1f50 == '\0') {
        if (cVar1 == '\n') {
          FUN_00551240();
          uVar3 = param_2;
        }
        else if (cVar1 == 'D') {
          FUN_00550820(1);
          uVar3 = param_2;
        }
        else if (cVar1 == 'E') {
          FUN_00550820(0xffffffff);
          uVar3 = param_2;
        }
        else if (cVar1 == 'F') {
          FUN_00550968(*(undefined4 *)(param_1 + 2));
          uVar3 = param_2;
        }
        else if ((cVar1 == 'H') && (iVar2 = FUN_0045a568(), uVar3 = param_2, iVar2 == 1)) {
          FUN_00464c36(4,0,0,0);
          uVar3 = param_2;
        }
      }
      else {
        ui_common_api_fn_00509ca2(*_DAT_004e1f54,param_1,6,param_4,param_2,param_3,param_4);
        uVar3 = param_2;
      }
    }
    else if (*param_1 == '\x04') {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar3 = 0xeb;
        FUN_0043d574(3,PTR_s_message_notify_page_004e1f3c,
                     PTR_s_D__01_workspace_s200_ap510b_iar__004e1f38,
                     PTR_s_MessageNotify_ReflashEventHandle_004e1f5c,0xeb,
                     PTR_s_MSG_NOTIF_EVENT_BASICINFO_UPDATE_004e1f58,param_1[1]);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__message_notify_page_MSG_NOTIF_E_004e1f60,
                            PTR_s__message_notify_page_MSG_NOTIF_E_004e1f60,param_1[1]);
      }
      if (param_1[1] == '\x01') {
        if (*_DAT_004e1f50 == '\0') {
          FUN_005511ce(*_DAT_004e1f4c);
        }
        else {
          ui_common_api_fn_00509ca2(*_DAT_004e1f54,param_1,param_2 & 0xffff);
        }
      }
    }
  }
  return (ulonglong)uVar3 << 0x20;
}

