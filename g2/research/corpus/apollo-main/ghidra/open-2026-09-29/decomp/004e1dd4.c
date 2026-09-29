
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_004e1dd4(int param_1,uint param_2,int param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 uVar4;
  
  puVar1 = _DAT_004e1f28;
  if (param_1 == 2) {
    uVar4 = param_4;
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x103;
      FUN_0043d574(4,PTR_s_message_notify_page_004e1f3c,
                   PTR_s_D__01_workspace_s200_ap510b_iar__004e1f38,
                   PTR_s_MessageNotify_ui_event_handler_004e1f68,0x103,
                   PTR_s_UI_EVENT_TYPE_INIT_004e1f64,uVar4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__message_notify_page_UI_EVENT_TY_004e1f6c,
                          PTR_s__message_notify_page_UI_EVENT_TY_004e1f6c);
    }
    puVar1 = _DAT_004e1f28;
    FUN_0043c0e4(_DAT_004e1f28,3,0);
    *puVar1 = 1;
    puVar2 = _DAT_004e1f4c;
    uVar4 = FUN_0043de82(param_4);
    *puVar2 = uVar4;
    *(undefined4 *)(_DAT_004e1f70 + 4) = *puVar2;
    FUN_0055225c(*puVar2);
    if (*DAT_004e1f2c == '\x01') {
      *DAT_004e1f2c = '\0';
      puVar1[2] = 1;
      FUN_005528b8();
      if (param_3 != 0) {
        FUN_00552ab0();
      }
    }
    else if (*DAT_004e1f2c == '\x02') {
      *DAT_004e1f2c = '\0';
      puVar1[2] = 0;
      FUN_00552906();
    }
    goto LAB_004e1f24;
  }
  if (param_1 == 3) {
    *_DAT_004e1f28 = 2;
    FUN_004e1cc4(param_2,param_3);
    if (*DAT_004e1f2c == '\x01') {
      *DAT_004e1f2c = '\0';
      puVar1[2] = 1;
      FUN_005528b8();
    }
    else if (*DAT_004e1f2c == '\x02') {
      *DAT_004e1f2c = '\0';
      puVar1[2] = 0;
      FUN_00552906();
    }
    if (puVar1[2] == '\x01') {
      FUN_00552ab0();
    }
    goto LAB_004e1f24;
  }
  if (param_1 == 4) {
    iVar3 = FUN_005529e4();
    if (iVar3 != 0) {
      FUN_00552a4a();
    }
    goto LAB_004e1f24;
  }
  if (param_1 != 5) goto LAB_004e1f24;
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    param_2 = 0x134;
    FUN_0043d574(3,PTR_s_message_notify_page_004e1f3c,
                 PTR_s_D__01_workspace_s200_ap510b_iar__004e1f38,
                 PTR_s_MessageNotify_ui_event_handler_004e1f68,0x134,_DAT_004e1f74);
  }
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1f < 0) {
LAB_004e1efe:
    compress_log_output(0xc000000,_DAT_004e1f78,_DAT_004e1f78);
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1d < 0) goto LAB_004e1efe;
  }
  FUN_00552906();
  FUN_0043c0e4(_DAT_004e1f28,3,0);
  *DAT_004e1f2c = '\0';
  FUN_00552820();
LAB_004e1f24:
  return (ulonglong)param_2 << 0x20;
}

