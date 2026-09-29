
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
system_close_page_event_handler
          (undefined4 param_1,undefined4 param_2,undefined1 *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined1 *puVar2;
  undefined1 *puVar3;
  
  puVar2 = param_3;
  puVar3 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_2 = 0xf2;
    puVar2 = PTR_s_received_event___d_0046aac0;
    puVar3 = param_3;
    FUN_0043d574(4,DAT_0046a834,DAT_0046a830,PTR_s_system_close_page_event_handler_0046aac4,0xf2,
                 PTR_s_received_event___d_0046aac0,param_3);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__system_close_received_event___d_0046aac8,
                        PTR_s__system_close_received_event___d_0046aac8,param_3,param_2,puVar2,
                        puVar3);
  }
  if (param_3 == (undefined1 *)0xa) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0xf4;
      FUN_0043d574(4,DAT_0046a834,DAT_0046a830,PTR_s_system_close_page_event_handler_0046aac4,0xf4,
                   PTR_s_LV_EVENT_CLICKED_0046aacc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__system_close_LV_EVENT_CLICKED_0046aad0,
                          PTR_s__system_close_LV_EVENT_CLICKED_0046aad0);
    }
    iVar1 = FUN_0045a568();
    if ((iVar1 != 2) && (iVar1 = FUN_0045a568(), iVar1 == 1)) {
      system_close_handle_click();
    }
  }
  else if (param_3 == &SUB_00000048) {
    iVar1 = FUN_0045a568();
    if (iVar1 != 2) {
      system_close_dispatch_page_action_00469e66(0x48,param_4);
    }
  }
  else if (param_3 == (undefined1 *)0x44) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x105;
      FUN_0043d574(4,DAT_0046a834,DAT_0046a830,PTR_s_system_close_page_event_handler_0046aac4,0x105,
                   PTR_s_SCROLLUP_EVENT_0046aad4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__system_close_SCROLLUP_EVENT_0046aad8,
                          PTR_s__system_close_SCROLLUP_EVENT_0046aad8);
    }
    iVar1 = FUN_0045a568();
    if (iVar1 != 2) {
      system_close_dispatch_page_action_00469e66(0x44,param_4);
    }
  }
  else if (param_3 == (undefined1 *)0x45) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x10d;
      FUN_0043d574(4,DAT_0046a834,DAT_0046a830,PTR_s_system_close_page_event_handler_0046aac4,0x10d,
                   PTR_s_SCROLLDOWN_EVENT_0046aadc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__system_close_SCROLLDOWN_EVENT_0046aae0,
                          PTR_s__system_close_SCROLLDOWN_EVENT_0046aae0);
    }
    iVar1 = FUN_0045a568();
    if (iVar1 != 2) {
      system_close_dispatch_page_action_00469e66(0x45,param_4);
    }
  }
  else if (((param_3 != (undefined1 *)0x4d) && (param_3 != (undefined1 *)0x4e)) && (param_3 == &IRQ)
          ) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x11c;
      FUN_0043d574(4,DAT_0046a834,DAT_0046a830,PTR_s_system_close_page_event_handler_0046aac4,0x11c,
                   PTR_s_IMU_Reflash_Event__0046aae4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,_DAT_0046ae6c,_DAT_0046ae6c);
    }
  }
  return CONCAT44(param_2,1);
}

