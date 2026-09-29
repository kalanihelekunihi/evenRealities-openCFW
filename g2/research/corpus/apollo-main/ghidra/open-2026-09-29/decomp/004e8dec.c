
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_004e8dec(char *param_1,uint param_2)

{
  char cVar1;
  byte bVar2;
  undefined1 uVar3;
  int iVar4;
  
  if (*DAT_004e939c == 1) {
    FUN_004e84b0(param_1);
  }
  else {
    cVar1 = *param_1;
    if (cVar1 == '\0') {
      if (*DAT_004e9390 == 0) {
        FUN_004e8bcc(param_1[1],*(undefined4 *)(param_1 + 2));
      }
      else {
        ui_common_api_fn_00509ca2(*_DAT_004e93e0,param_1 + 1,5);
      }
    }
    else if (cVar1 == '\x01') {
      FUN_004e8970(param_1 + 1,param_2 - 1);
    }
    else if (cVar1 == '\x02') {
      FUN_004ed9b6(param_1 + 1,param_2 - 1);
    }
    else if (cVar1 != '\x03') {
      if (cVar1 == '\x04') {
        FUN_004ebf5c(param_1 + 1,param_2 - 1);
      }
      else if (cVar1 == '\x05') {
        FUN_004f8644(param_1 + 1,param_2 - 1);
      }
      else if (cVar1 == '\x06') {
        FUN_004fb5e8(param_1 + 1,param_2 - 1);
        dashboard_watchface_manager_call_30();
      }
      else if (cVar1 == '\a') {
        if (param_2 < 4) {
          cVar1 = param_1[1];
        }
        else {
          cVar1 = param_1[3];
        }
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004e9370,DAT_004e936c,PTR_s_Dashboard_ReflashEventHandler_004e93cc,
                       0x5d9,DAT_004e9350,param_1[1],param_1[2],cVar1);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xcc00000,DAT_004e9354,DAT_004e9354,param_1[1],param_1[2],cVar1);
        }
        dashboard_watchface_manager_call_0c(param_1[1],param_1[2],cVar1);
      }
      else if (cVar1 == '\b') {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004e9370,DAT_004e936c,PTR_s_Dashboard_ReflashEventHandler_004e93cc,
                       0x5de,DAT_004e9230);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_004e9234,DAT_004e9234);
        }
        FUN_004e8a90();
      }
      else if (cVar1 == '\t') {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004e9370,DAT_004e936c,PTR_s_Dashboard_ReflashEventHandler_004e93cc,
                       0x5e3,DAT_004e9238);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004e9270,DAT_004e9270);
        }
        cVar1 = param_1[1];
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004e9370,DAT_004e936c,PTR_s_Dashboard_ReflashEventHandler_004e93cc,
                       0x5e5,DAT_004e9274,cVar1);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_004e9278,DAT_004e9278,cVar1);
        }
        dashboard_watchface_manager_call_20(cVar1);
      }
      else if (cVar1 == '\n') {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004e9370,DAT_004e936c,PTR_s_Dashboard_ReflashEventHandler_004e93cc,
                       0x5ea,DAT_004e927c);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004e92e8,DAT_004e92e8);
        }
        cVar1 = param_1[1];
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004e9370,DAT_004e936c,PTR_s_Dashboard_ReflashEventHandler_004e93cc,
                       0x5ec,DAT_004e92ec,cVar1);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_004e92f0,DAT_004e92f0,cVar1);
        }
        FUN_004efcb8(cVar1);
      }
      else if (cVar1 == '\x0f') {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004e9370,DAT_004e936c,PTR_s_Dashboard_ReflashEventHandler_004e93cc,
                       0x59f,PTR_s_receive_DASHBOARD_NEWS_LOAD_CONT_004e93c8);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xc000000,PTR_s__dashborad_ui_receive_DASHBOARD__004e93d0);
        }
        if (*_DAT_004e93d4 == 1) {
          FUN_004efffc();
        }
      }
      else if (cVar1 == '\x12') {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004e9370,DAT_004e936c,PTR_s_Dashboard_ReflashEventHandler_004e93cc,
                       0x5a7,_DAT_004e93d8);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xc000000,_DAT_004e93dc,_DAT_004e93dc);
        }
        if (*_DAT_004e93d4 == 1) {
          FUN_004efffc();
        }
      }
      else if (cVar1 == '\x13') {
        bVar2 = param_1[1];
        cVar1 = param_1[2];
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004e9370,DAT_004e936c,PTR_s_Dashboard_ReflashEventHandler_004e93cc,
                       0x5fe,PTR_s_ring_status_change__sub__d_data__004e9ce8,bVar2,cVar1);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xc800000,PTR_s__dashborad_ui_ring_status_change_004e9cec,
                              PTR_s__dashborad_ui_ring_status_change_004e9cec,bVar2,cVar1);
        }
        if (bVar2 == 0) {
          dashboard_watchface_manager_call_24(0,0);
        }
        else if (bVar2 == 2) {
          dashboard_watchface_manager_call_28(0);
        }
        else if (bVar2 < 2) {
          uVar3 = FUN_0049c5bc();
          dashboard_watchface_manager_call_24(1,uVar3);
        }
        else if (bVar2 == 4) {
          dashboard_watchface_manager_call_2c(cVar1);
        }
        else if (bVar2 < 4) {
          dashboard_watchface_manager_call_28(1);
        }
        else {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(2,DAT_004e9370,DAT_004e936c,PTR_s_Dashboard_ReflashEventHandler_004e93cc,
                         0x611,PTR_s_unknown_ring_sub_event__d_004e9cf0,bVar2);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x8400000,PTR_s__dashborad_ui_unknown_ring_sub_e_004e9cf4,
                                PTR_s__dashborad_ui_unknown_ring_sub_e_004e9cf4,bVar2);
          }
        }
      }
    }
  }
  return 0;
}

