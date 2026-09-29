
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_004e2c40(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  char *pcVar2;
  int iVar3;
  undefined4 uVar4;
  
  if (param_1 != 2) {
    if (param_1 == 3) {
      FUN_004e2ad6(param_2,param_3);
      goto LAB_004e2d68;
    }
    if (param_1 == 4) {
      even_ai_stream_on_auto_reflash();
      FUN_005538d8();
      even_ai_timer_process_all();
      goto LAB_004e2d68;
    }
    if (param_1 != 5) goto LAB_004e2d68;
    func_0x00497db4();
    pcVar2 = _DAT_004e2e04;
    if ((*_DAT_004e2e04 != '\x06') || ((_DAT_004e2e04[1] != '\x02' && (_DAT_004e2e04[1] != '\x04')))
       ) {
      service_even_ai_fn_004982d4(3);
    }
    AUDM_appRelease(3);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x376;
      FUN_0043d574(3,PTR_s_even_ai_page_004e2df8,PTR_s_D__01_workspace_s200_ap510b_iar__004e2df4,
                   PTR_s_EvenAI_ui_event_handler_004e2df0,0x376,_DAT_004e2e08);
    }
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1f < 0) {
LAB_004e2d1c:
      compress_log_output(0xc000000,_DAT_004e2e0c,_DAT_004e2e0c);
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1d < 0) goto LAB_004e2d1c;
    }
    FUN_004e1fa6();
    even_ai_timer_deinit_all();
    FUN_0043c0e4(pcVar2,0x210,0);
    FUN_0043c0e4(_DAT_004e2d7c,0x400,0);
    FUN_0043c0e4(_DAT_004e2d80,0x400,0);
    FUN_004e1fbe();
    even_ai_page_deinit();
    ble_param_reset_delayed_event(10000);
    goto LAB_004e2d68;
  }
  uVar4 = param_4;
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    param_2 = 0x353;
    FUN_0043d574(4,PTR_s_even_ai_page_004e2df8,PTR_s_D__01_workspace_s200_ap510b_iar__004e2df4,
                 PTR_s_EvenAI_ui_event_handler_004e2df0,0x353,PTR_s_UI_EVENT_TYPE_INIT_004e2dec,
                 uVar4);
  }
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1f < 0) {
LAB_004e2c78:
    compress_log_output(0x10000000,PTR_s__even_ai_page_UI_EVENT_TYPE_INIT_004e2dfc,
                        PTR_s__even_ai_page_UI_EVENT_TYPE_INIT_004e2dfc);
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1d < 0) goto LAB_004e2c78;
  }
  FUN_004e1f7c();
  ble_state_skip_manual_start(0);
  puVar1 = _DAT_004e2de0;
  uVar4 = FUN_0043de82(param_4);
  *puVar1 = uVar4;
  *(undefined4 *)(_DAT_004e2e00 + 4) = *puVar1;
  even_ai_page_init(*puVar1);
LAB_004e2d68:
  return (ulonglong)param_2 << 0x20;
}

