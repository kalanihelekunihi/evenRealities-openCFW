
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_004ac278(int param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  char *pcVar3;
  int iVar4;
  
  pcVar3 = _DAT_004acb20;
  if ((param_1 == 0) || (*(short *)(param_1 + 2) == 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 299;
      param_2 = PTR_s_box_rcv_msg_err_004acb38;
      FUN_0043d574(1,PTR_s_box_detect_004ac81c,DAT_004ac818,_DAT_004acd4c,299,
                   PTR_s_box_rcv_msg_err_004acb38,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__box_detect_box_rcv_msg_err_004acb3c,
                          PTR_s__box_detect_box_rcv_msg_err_004acb3c);
    }
  }
  else {
    bVar1 = *(byte *)(param_1 + 4);
    if (bVar1 == 0) {
      pcVar3 = (char *)FUN_0050938e(0);
      if ((*pcVar3 == '\x01') && (iVar2 = FUN_00510fe2(_DAT_004acd50), iVar2 != _DAT_004acd54)) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          param_1 = 0x13a;
          param_2 = PTR_s_npmx_interrupt_handler_failed____004acd58;
          FUN_0043d574(1,PTR_s_box_detect_004ac81c,DAT_004ac818,_DAT_004acd4c,0x13a,
                       PTR_s_npmx_interrupt_handler_failed____004acd58,iVar2);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x4400000,PTR_s__box_detect_npmx_interrupt_handl_004acd5c,
                              PTR_s__box_detect_npmx_interrupt_handl_004acd5c,iVar2);
        }
      }
    }
    else if (bVar1 == 2) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_1 = 0x146;
        param_2 = PTR_s_glasses_wear__update_state_to_ou_004acd60;
        FUN_0043d574(3,PTR_s_box_detect_004ac81c,DAT_004ac818,_DAT_004acd4c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__box_detect_glasses_wear__update_004acd64,
                            PTR_s__box_detect_glasses_wear__update_004acd64);
      }
      FUN_004abfba();
      iVar2 = DAT_004acafc;
      if (*(char *)(DAT_004acafc + 3) != '\0') {
        *(undefined1 *)(DAT_004acafc + 3) = 0;
      }
      FUN_004ac19c(1);
      if (*(char *)(iVar2 + 2) != '\0') {
        *(undefined1 *)(iVar2 + 2) = 0;
      }
      FUN_004ac798();
    }
    else if (bVar1 < 2) {
      FUN_004abfba();
      FUN_004abfac(0);
      FUN_004ac19c(0);
    }
    else if (bVar1 == 4) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_1 = 0x160;
        param_2 = PTR_s__Box__Ring_established_then_clos_004acd70;
        FUN_0043d574(3,PTR_s_box_detect_004ac81c,DAT_004ac818,_DAT_004acd4c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__box_detect__Box__Ring_establish_004acd74,
                            PTR_s__box_detect__Box__Ring_establish_004acd74);
      }
      *_DAT_004acb24 = 0;
      *_DAT_004acb20 = '\0';
      if (*_DAT_004acb08 != 0) {
        osTimerStop(*_DAT_004acb08);
      }
    }
    else if (bVar1 < 4) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_1 = 0x157;
        param_2 = PTR_s__Box__Ring_connected_004acd68;
        FUN_0043d574(3,PTR_s_box_detect_004ac81c,DAT_004ac818,_DAT_004acd4c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__box_detect__Box__Ring_connected_004acd6c,
                            PTR_s__box_detect__Box__Ring_connected_004acd6c);
      }
      *_DAT_004acb24 = 1;
      if (*_DAT_004acb08 != 0) {
        osTimerStop(*_DAT_004acb08);
      }
    }
    else if (bVar1 == 6) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_1 = 0x16e;
        param_2 = PTR_s__Box__Ring_connect_event_cancell_004acd80;
        FUN_0043d574(3,PTR_s_box_detect_004ac81c,DAT_004ac818,_DAT_004acd4c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__box_detect__Box__Ring_connect_e_004acd84,
                            PTR_s__box_detect__Box__Ring_connect_e_004acd84);
      }
      *_DAT_004acb20 = '\0';
      if (*_DAT_004acb08 != 0) {
        osTimerStop(*_DAT_004acb08);
      }
    }
    else if (bVar1 < 6) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_1 = 0x169;
        param_2 = PTR_s__Box__Ring_connect_attempt_faile_004acd78;
        FUN_0043d574(3,PTR_s_box_detect_004ac81c,DAT_004ac818,_DAT_004acd4c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__box_detect__Box__Ring_connect_a_004acd7c,
                            PTR_s__box_detect__Box__Ring_connect_a_004acd7c);
      }
      *_DAT_004acb24 = 0;
    }
    else if ((bVar1 == 7) && (*_DAT_004acb20 != '\0')) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_1 = 0x177;
        param_2 = PTR_s__Box__Ring_reconnect_trigger_tim_004acd88;
        FUN_0043d574(2,PTR_s_box_detect_004ac81c,DAT_004ac818,_DAT_004acd4c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__box_detect__Box__Ring_reconnect_004acd8c,
                            PTR_s__box_detect__Box__Ring_reconnect_004acd8c);
      }
      *pcVar3 = '\0';
      APP_MasterResetSceneConnectPending();
    }
  }
  return CONCAT44(param_2,param_1);
}

