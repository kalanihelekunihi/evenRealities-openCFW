
void bleProcMsg(undefined2 *param_1)

{
  char cVar1;
  char cVar2;
  undefined4 uVar3;
  int iVar4;
  char cVar5;
  
  uVar3 = DAT_004b843c;
  cVar5 = '\0';
  cVar1 = *(char *)(param_1 + 1);
  cVar2 = (char)*param_1;
  if (cVar1 == '\x12') {
    thread_ble_wsf_tx_complete_notify();
    if (*(char *)((int)param_1 + 3) != '\0') {
      if (*(char *)((int)param_1 + 3) == 'r') {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(2,DAT_004b8210,DAT_004b820c,DAT_004b8200,0x187,DAT_004b8134,cVar2);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_004b8138,DAT_004b8138,cVar2);
        }
      }
      else {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004b8210,DAT_004b820c,DAT_004b8200,0x18b,DAT_004b813c,
                       *(undefined1 *)((int)param_1 + 3),cVar2);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_004b81b0,DAT_004b81b0,*(undefined1 *)((int)param_1 + 3),
                              cVar2);
        }
      }
    }
  }
  else if (cVar1 != '\x15') {
    if (cVar1 == ' ') {
      attsCsfSetHashUpdateStatus(1);
      if ((int)((uint)*DAT_004b81b4 << 0x1c) < 0) {
        DmSecGenerateEccKeyReq();
      }
      else {
        AttsCalculateDbHash();
      }
      cVar5 = '\x01';
    }
    else if (cVar1 == '\'') {
      iVar4 = DmConnRole(cVar2);
      if (iVar4 == 1) {
        pairMgrSecAuthFlagSet(0);
        PB_LastTxEncodeRingConnectInfoTimeSet(0);
      }
      thread_ble_wsf_tx_complete_notify();
      iVar4 = FUN_004bb07c(cVar2);
      if (iVar4 != 0) {
        FUN_0047b488(iVar4,0);
        FUN_0047b3cc(iVar4,0);
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004b8210,DAT_004b820c,DAT_004b8200,0x1b2,DAT_004b8214);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004b8218,DAT_004b8218);
        }
      }
      cVar5 = '\b';
    }
    else if (cVar1 == '(') {
      *DAT_004b82d4 = 0;
      thread_ble_wsf_tx_complete_notify();
      fw_event_loop_remove_delayed(DAT_004b821c);
      fw_event_loop_remove_delayed(&LAB_004b81b8_1);
      iVar4 = DmConnRole(cVar2);
      if (iVar4 == 1) {
        pairMgrSecAuthFlagSet(0);
      }
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        uVar3 = FUN_004b848c(*(undefined1 *)(param_1 + 4));
        FUN_0043d574(1,DAT_004b8210,DAT_004b820c,DAT_004b8200,0x1db,DAT_004b8220,cVar2,
                     *(undefined1 *)(param_1 + 4),uVar3);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        uVar3 = FUN_004b848c(*(undefined1 *)(param_1 + 4));
        compress_log_output(0x4c00000,DAT_004b82d8,DAT_004b82d8,cVar2,*(undefined1 *)(param_1 + 4),
                            uVar3);
      }
      if (*(char *)(param_1 + 4) == '=') {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004b8210,DAT_004b820c,DAT_004b8200,0x1df,DAT_004b82dc,cVar2);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_004b82e0,DAT_004b82e0,cVar2);
        }
      }
      cVar5 = '\t';
    }
    else if (cVar1 == '*') {
      DmSecGenerateEccKeyReq();
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004b8210,DAT_004b820c,DAT_004b8200,0x1f1,DAT_004b837c,cVar2);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004b8380,DAT_004b8380,cVar2);
      }
      iVar4 = FUN_004bb07c(cVar2);
      if (iVar4 != 0) {
        FUN_0047c084();
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004b8210,DAT_004b820c,DAT_004b8200,0x1f7,DAT_004b8384);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_004b8388,DAT_004b8388);
        }
        FUN_0047bc30();
      }
      cVar5 = '\n';
    }
    else if (cVar1 == '+') {
      fw_event_loop_remove_delayed(DAT_004b843c);
      fw_event_loop_push_delayed(uVar3,0,10);
      DmSecGenerateEccKeyReq();
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        uVar3 = FUN_004b8390(*(undefined1 *)((int)param_1 + 3));
        FUN_0043d574(1,DAT_004b8210,DAT_004b820c,DAT_004b8200,0x212,DAT_004b8440,
                     *(undefined1 *)((int)param_1 + 3),uVar3);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        uVar3 = FUN_004b8390(*(undefined1 *)((int)param_1 + 3));
        compress_log_output(0x4800000,DAT_004b8444,DAT_004b8444,*(undefined1 *)((int)param_1 + 3),
                            uVar3);
      }
      FUN_0047c568(cVar2,*(undefined1 *)((int)param_1 + 3));
      cVar5 = '\v';
    }
    else if (cVar1 == ',') {
      iVar4 = FUN_004bb07c(cVar2);
      if (iVar4 != 0) {
        FUN_0047b488(iVar4,0);
        FUN_0047b3cc(iVar4,0);
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004b8210,DAT_004b820c,DAT_004b8200,0x222,DAT_004b8448);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004b844c,DAT_004b844c);
        }
      }
      if ((cVar2 != '\0') && (iVar4 = DmConnRole(cVar2), uVar3 = DAT_004b821c, iVar4 == 1)) {
        fw_event_loop_remove_delayed(DAT_004b821c);
        fw_event_loop_push_delayed(uVar3,cVar2,1000);
      }
      FUN_004b82e8(1);
      iVar4 = pairMgrSecAuthFlagGet();
      uVar3 = DAT_004b843c;
      if (iVar4 == 0) {
        pairMgrSecAuthFlagSet(1);
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004b8210,DAT_004b820c,DAT_004b8200,0x232,DAT_004b8458,cVar2);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_004b845c,DAT_004b845c,cVar2);
        }
      }
      else {
        fw_event_loop_remove_delayed(DAT_004b843c);
        fw_event_loop_push_delayed(uVar3,1,200);
        fw_event_loop_push_delayed(uVar3,1,1000);
        fw_event_loop_push_delayed(uVar3,1,2000);
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004b8210,DAT_004b820c,DAT_004b8200,0x22f,DAT_004b8450,cVar2);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_004b8454,DAT_004b8454,cVar2);
        }
      }
      uVar3 = osKernelGetTickCount();
      *DAT_004b82d4 = uVar3;
      iVar4 = DmConnRole(cVar2);
      if (iVar4 == 0) {
        Thread_SendEvtToRingTask(0x10);
      }
      cVar5 = '\f';
    }
    else if (cVar1 == '-') {
      cVar5 = '\r';
    }
    else if (cVar1 == '.') {
      FUN_004bafda(param_1);
    }
    else if (cVar1 == '4') {
      DmSecSetEccKey(param_1 + 2);
      iVar4 = attsCsfGetHashUpdateStatus();
      if (iVar4 != 0) {
        AttsCalculateDbHash();
      }
    }
    else if (cVar1 == '5') {
      FUN_004bb030(param_1);
    }
    else if (cVar1 == '<') {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004b8210,DAT_004b820c,DAT_004b8200,0x251,DAT_004b8460,
                     *(undefined1 *)((int)param_1 + 3));
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004b8464,DAT_004b8464,*(undefined1 *)((int)param_1 + 3));
      }
    }
    else if (cVar1 == 'F') {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(3,DAT_004b8210,DAT_004b820c,DAT_004b8200,0x1ec,DAT_004b82e4,
                     *(undefined1 *)(param_1 + 2),*(undefined1 *)((int)param_1 + 9),
                     *(undefined1 *)(param_1 + 4));
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xcc00000,DAT_004b8378,DAT_004b8378,*(undefined1 *)(param_1 + 2),
                            *(undefined1 *)((int)param_1 + 9),*(undefined1 *)(param_1 + 4));
      }
    }
    else if (cVar1 == 'y') {
      cVar5 = '\x1e';
    }
    else if (cVar1 == -0x5b) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004b8210,DAT_004b820c,DAT_004b8200,0x201,DAT_004b838c,cVar2);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004b8438,DAT_004b8438,cVar2);
      }
      if (cVar2 != '\0') {
        FUN_00531d60(cVar2);
      }
    }
    else if (cVar1 == -0x5a) {
      HciDrvRadioBoot(0);
      DmDevReset();
    }
    else if (cVar1 == -0x44) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004b8210,DAT_004b820c,DAT_004b8200,0x259,DAT_004b8468,
                     *(undefined1 *)(DAT_004b81fc + 0x54),*(undefined1 *)(DAT_004b81fc + 0x55));
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_004b846c,DAT_004b846c,
                            *(undefined1 *)(DAT_004b81fc + 0x54),
                            *(undefined1 *)(DAT_004b81fc + 0x55));
      }
      slave_sync_connection_status_0046f32c();
      if (*(char *)(DAT_004b81fc + 0x55) != '\0') {
        fw_event_loop_remove_delayed(DAT_004b8470);
        PB_TxEncodeNotifyRingConnectInfo(0);
        uVar3 = DAT_004b8474;
        fw_event_loop_remove_delayed(DAT_004b8474);
        fw_event_loop_push_delayed(uVar3,0,10000);
      }
    }
  }
  if (cVar5 != '\0') {
    FUN_004bd054(cVar5);
  }
  return;
}

