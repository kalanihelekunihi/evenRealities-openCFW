
/* WARNING: Removing unreachable block (ram,0x005b0862) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_005b06aa(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  longlong lVar1;
  char *pcVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uStack_30;
  undefined *puStack_2c;
  undefined1 auStack_28 [4];
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  
  uStack_18 = param_4;
  FUN_0043c0e4(auStack_28,8,0);
  FUN_005b01ca();
  if (param_1 == 2) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      puStack_2c = PTR_s_Conversate_display_startup_005b0a7c;
      uStack_30 = 0x10a;
      FUN_0043d574(3,DAT_005b09f4,DAT_005b09f0,PTR_s_Conversate_ui_event_handler_005b0a80);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__conversate_Conversate_display_s_005b0a84,
                          PTR_s__conversate_Conversate_display_s_005b0a84);
    }
    iVar3 = osKernelGetTickCount();
    *_DAT_005b0a88 = iVar3;
    if (*_DAT_005b0a8c == '\0') {
      auStack_28[0] = 1;
    }
    else {
      auStack_28[0] = 3;
    }
    ble_state_skip_manual_start(0);
    FUN_005b03c2();
    FUN_005b14ce(param_4);
    FUN_005b1724(auStack_28[0],uStack_24);
    *(undefined4 *)(_DAT_005b0a94 + 4) = *_DAT_005b0a90;
  }
  else if (1 < param_1) {
    if (param_1 == 4) {
      FUN_005b03d8();
      func_0x005b23ae();
      FUN_005b3d62();
    }
    else if (param_1 < 4) {
      FUN_00439be4(auStack_28,param_2,8);
      FUN_005b1724(auStack_28[0],uStack_24);
    }
    else if (param_1 == 5) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        puStack_2c = PTR_s_Conversate_display_exit_005b0a98;
        uStack_30 = 0x122;
        FUN_0043d574(3,DAT_005b09f4,DAT_005b09f0,PTR_s_Conversate_ui_event_handler_005b0a80);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__conversate_Conversate_display_e_005b0a9c,
                            PTR_s__conversate_Conversate_display_e_005b0a9c);
      }
      func_0x005b43d4();
      func_0x005b473a();
      func_0x005b430e();
      FUN_0059624e();
      FUN_005b156c();
      AUDM_appRelease(4);
      ble_param_reset_delayed_event(10000);
      pcVar2 = _DAT_005b0a8c;
      if (*_DAT_005b0a8c == '\x01') {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          puStack_2c = PTR_s_notify_app_to_close_005b0aa0;
          uStack_30 = 300;
          FUN_0043d574(3,DAT_005b09f4,DAT_005b09f0,PTR_s_Conversate_ui_event_handler_005b0a80);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0xc000000,PTR_s__conversate_notify_app_to_close_005b0aa4,
                              PTR_s__conversate_notify_app_to_close_005b0aa4);
        }
        FUN_0043c0e4(&uStack_30,2,0);
        uStack_30 = CONCAT22(uStack_30._2_2_,2);
        APP_PbConversateTxEncodeNotify(&uStack_30);
      }
      FUN_0043c0e4(pcVar2,6,0);
      iVar3 = osKernelGetTickCount();
      lVar1 = (ulonglong)(uint)(iVar3 - *_DAT_005b0a88) * 1000;
      uVar4 = FUN_0047cc60((int)lVar1,(int)((ulonglong)lVar1 >> 0x20),1000,0);
      iVar3 = FUN_0045a568();
      if (iVar3 == 1) {
        uStack_20 = *(undefined4 *)PTR_DAT_005b0aa8;
        uStack_1c = uVar4;
        FUN_0048eb32(_DAT_005b0aac,2,&uStack_20);
      }
    }
  }
  FUN_005b0284();
  return;
}

