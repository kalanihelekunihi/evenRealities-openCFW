
void _masterProcMsg(undefined2 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  ushort uVar2;
  undefined2 uVar3;
  char cVar4;
  ushort uVar5;
  char *pcVar6;
  int *piVar7;
  undefined1 uVar8;
  undefined4 uVar9;
  byte *pbVar10;
  int iVar11;
  int iVar12;
  uint local_2c;
  uint local_28;
  uint local_24;
  uint local_20;
  undefined4 uStack_1c;
  
  piVar7 = DAT_004a1b54;
  cVar1 = *(char *)(param_1 + 1);
  cVar4 = (char)*param_1;
  uStack_1c = param_4;
  if (cVar1 != '\x05') {
    if ((cVar1 == '\t') || (cVar1 == '\n')) {
      if (cVar4 == '\0') {
        return;
      }
      iVar11 = DmConnRole(cVar4);
      if (iVar11 != 0) {
        return;
      }
      iVar11 = FUN_0043d0ce();
      if (iVar11 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004a0fd0,DAT_004a0fcc,DAT_004a148c,0x241,DAT_004a1488);
      }
      iVar11 = FUN_0043d0ce();
      if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004a1490,DAT_004a1490);
      }
      thread_ble_wsf_tx_complete_notify();
      return;
    }
    if ((cVar1 != '\r') && (cVar1 != '\x0e')) {
      if (cVar1 == '\x15') {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004a0fd0,DAT_004a0fcc,DAT_004a148c,0x256,DAT_004a1524);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004a1528,DAT_004a1528);
        }
        ring_master_reconnect(param_1);
        return;
      }
      if (cVar1 == '\x16') {
        if (cVar4 == '\0') {
          return;
        }
        iVar11 = DmConnRole(cVar4);
        piVar7 = DAT_004a15a0;
        if (iVar11 != 0) {
          return;
        }
        *(undefined2 *)(*DAT_004a15a0 + 0x24) = param_1[7];
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004a0fd0,DAT_004a0fcc,DAT_004a148c,0x25d,DAT_004a15a4,
                       *(undefined2 *)(*piVar7 + 0x24));
        }
        iVar11 = FUN_0043d0ce();
        if ((-1 < iVar11 << 0x1f) && (iVar11 = FUN_0043d0ce(), -1 < iVar11 << 0x1d)) {
          return;
        }
        compress_log_output(0x10400000,DAT_004a15a8,DAT_004a15a8,*(undefined2 *)(*piVar7 + 0x24));
        return;
      }
      if (cVar1 == '$') {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004a0fd0,DAT_004a0fcc,DAT_004a148c,0x247,DAT_004a1494);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004a1518);
        }
        ring_master_scan_start(param_1);
        return;
      }
      if (cVar1 == '%') {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004a0fd0,DAT_004a0fcc,DAT_004a148c,0x24c,DAT_004a151c);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004a1520,DAT_004a1520);
        }
        _bleMasterScanStop(param_1);
        return;
      }
      if (cVar1 == '&') {
        _bleMasterScanReport(param_1);
        return;
      }
      if (cVar1 == '\'') {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          uVar8 = DmConnRole(cVar4);
          FUN_0043d574(4,DAT_004a0fd0,DAT_004a0fcc,DAT_004a148c,0x262,DAT_004a15ac,cVar4,uVar8);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          uVar8 = DmConnRole(cVar4);
          compress_log_output(0x10800000,DAT_004a15b0,DAT_004a15b0,cVar4,uVar8);
        }
        if (cVar4 == '\0') {
          return;
        }
        iVar11 = DmConnRole(cVar4);
        if (iVar11 != 0) {
          return;
        }
        *DAT_004a152c = 0;
        *DAT_004a1168 = 0;
        _SetRingLinkState(2,DAT_004a1638);
        fw_event_loop_remove_delayed(DAT_004a116c);
        _bleMasterGetCB(param_1);
        if ((ushort)param_1[8] < 0x19) {
          iVar11 = osKernelGetTickCount();
          *DAT_004a163c = iVar11;
        }
        else {
          *DAT_004a163c = 0;
        }
        uVar9 = DAT_004a1530;
        fw_event_loop_remove_delayed(DAT_004a1530);
        fw_event_loop_push_delayed(uVar9,0,6000);
        uVar8 = FUN_0047a676(1);
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004a0fd0,DAT_004a0fcc,DAT_004a148c,0x277,DAT_004a1534,uVar8);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_004a1538,DAT_004a1538,uVar8);
        }
        DmConnReadRssi(cVar4);
        return;
      }
      if (cVar1 == '(') {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          uVar8 = DmConnRole(cVar4);
          FUN_0043d574(4,DAT_004a0fd0,DAT_004a0fcc,DAT_004a148c,0x298,DAT_004a1640,cVar4,uVar8);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          uVar8 = DmConnRole(cVar4);
          compress_log_output(0x10800000,DAT_004a1644,DAT_004a1644,cVar4,uVar8);
        }
        if (cVar4 == '\0') {
          return;
        }
        iVar11 = DmConnRole(cVar4);
        if (iVar11 != 0) {
          return;
        }
        RING_ConnectPolicyResetRingConnectInfoThrottle();
        cVar1 = *DAT_004a0fd4;
        *(undefined1 *)(*DAT_004a1218 + 0x55) = 0;
        *DAT_004a1168 = 0;
        *DAT_004a163c = 0;
        FUN_004728a0();
        fw_event_loop_remove_delayed(DAT_004a116c);
        if (*(char *)(param_1 + 4) == '\0') {
          uVar8 = 8;
        }
        else {
          uVar8 = *(undefined1 *)(param_1 + 4);
        }
        fw_event_loop_remove_delayed(DAT_004a1648);
        fw_event_loop_remove_delayed(DAT_004a1530);
        pcVar6 = DAT_004a1164;
        if ((cVar1 == '\x05') || (*DAT_004a1164 == '\0')) {
          if (cVar1 != '\x05') {
            iVar11 = FUN_0043d0ce();
            if (iVar11 << 0x1e < 0) {
              FUN_0043d574(3,DAT_004a0fd0,DAT_004a0fcc,DAT_004a148c,0x2b8,DAT_004a164c);
            }
            iVar11 = FUN_0043d0ce();
            if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
              compress_log_output(0xc000000,DAT_004a1650,DAT_004a1650);
            }
          }
        }
        else {
          FUN_004b82e8(2);
          *pcVar6 = '\0';
        }
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          uVar9 = _ringLinkStateName(cVar1);
          FUN_0043d574(3,DAT_004a0fd0,DAT_004a0fcc,DAT_004a148c,699,DAT_004a1654,cVar4,
                       *(undefined1 *)(param_1 + 4),uVar9);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          uVar9 = _ringLinkStateName(cVar1);
          compress_log_output(0xcc00000,DAT_004a1658,DAT_004a1658,cVar4,*(undefined1 *)(param_1 + 4)
                              ,uVar9);
        }
        if (cVar1 != '\x06') {
          _masterMaybeNotifyRingConnectFailure(uVar8);
          if (cVar1 == '\x03') {
            iVar11 = FUN_0043d0ce();
            if (iVar11 << 0x1e < 0) {
              FUN_0043d574(3,DAT_004a0fd0,DAT_004a0fcc,DAT_004a148c,0x2cc,DAT_004a1814);
            }
            iVar11 = FUN_0043d0ce();
            if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
              compress_log_output(0xc000000,DAT_004a1818,DAT_004a1818);
            }
            APP_MasterClearRingConnectFailureNotifyAfterRetry();
            *DAT_004a152c = 0;
            central_emit_ring_link_event_004a153c(4);
            *DAT_004a1160 = '\0';
            _SetRingLinkState(0,DAT_004a181c);
            return;
          }
          if (cVar1 == '\x04') {
            iVar11 = FUN_0043d0ce();
            if (iVar11 << 0x1e < 0) {
              FUN_0043d574(3,DAT_004a0fd0,DAT_004a0fcc,DAT_004a148c,0x2d3,DAT_004a1820);
            }
            iVar11 = FUN_0043d0ce();
            if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
              compress_log_output(0xc000000,DAT_004a1824,DAT_004a1824);
            }
            APP_MasterClearRingConnectFailureNotifyAfterRetry();
            *DAT_004a152c = 0;
            *DAT_004a1160 = '\0';
            _SetRingLinkState(0,DAT_004a1828);
            return;
          }
          if (cVar1 == '\x05') {
            iVar11 = FUN_0043d0ce();
            if (iVar11 << 0x1e < 0) {
              FUN_0043d574(3,DAT_004a0fd0,DAT_004a0fcc,DAT_004a148c,0x2dc,DAT_004a182c,*DAT_004a152c
                          );
            }
            iVar11 = FUN_0043d0ce();
            if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
              compress_log_output(0xc400000,DAT_004a1830,DAT_004a1830,*DAT_004a152c);
            }
          }
          else {
            iVar11 = FUN_0043d0ce();
            if (iVar11 << 0x1e < 0) {
              FUN_0043d574(3,DAT_004a0fd0,DAT_004a0fcc,DAT_004a148c,0x2df,DAT_004a1834,
                           *(undefined1 *)(param_1 + 4),*DAT_004a152c);
            }
            iVar11 = FUN_0043d0ce();
            if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
              compress_log_output(0xc800000,DAT_004a1838,DAT_004a1838,*(undefined1 *)(param_1 + 4),
                                  *DAT_004a152c);
            }
          }
          pcVar6 = DAT_004a1160;
          if (*DAT_004a1160 == '\0') {
            central_emit_ring_link_event_004a153c(5);
          }
          else {
            central_emit_ring_link_event_004a153c(4);
          }
          *pcVar6 = '\0';
          uVar9 = DAT_004a19bc;
          if (cVar1 == '\x05') {
            uVar9 = DAT_004a183c;
          }
          _SetRingLinkState(0,uVar9);
          _masterConnectEventRetry(uVar8);
          return;
        }
        iVar11 = AppMasterSecGetAddr();
        if (iVar11 != 0) {
          FUN_0047b59c(*(undefined1 *)(iVar11 + 6),iVar11);
        }
        AppMasterSecClearAddr();
        APP_MasterClearRingConnectFailureNotifyAfterRetry();
        *DAT_004a152c = 0;
        _SetRingLinkState(0,DAT_004a165c);
        return;
      }
      if (cVar1 == ')') {
        if (cVar4 == '\0') {
          return;
        }
        iVar11 = DmConnRole(cVar4);
        if (iVar11 != 0) {
          return;
        }
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004a0fd0,DAT_004a0fcc,DAT_004a148c,0x287,DAT_004a15b4,
                       *(undefined1 *)(param_1 + 2),param_1[4],
                       ((uint)(ushort)param_1[4] * 0x4e2) / 1000);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0xcc00000,DAT_004a15b8,DAT_004a15b8,*(undefined1 *)(param_1 + 2),
                              param_1[4],((uint)(ushort)param_1[4] * 0x4e2) / 1000);
        }
        piVar7 = DAT_004a163c;
        if (*(char *)(param_1 + 2) != '\0') {
          return;
        }
        if (0x18 < (ushort)param_1[4]) {
          if (*DAT_004a163c == 0) {
            return;
          }
          iVar11 = osKernelGetTickCount();
          local_2c = iVar11 - *piVar7;
          FUN_0048eb32(DAT_004a15bc,1,&local_2c);
          *piVar7 = 0;
          return;
        }
        if (*DAT_004a163c != 0) {
          return;
        }
        iVar11 = osKernelGetTickCount();
        *piVar7 = iVar11;
        return;
      }
      if (cVar1 == '-') {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004a1af4,DAT_004a1af0,DAT_004a148c,0x2ff,DAT_004a19ec);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004a19f0,DAT_004a19f0);
        }
        Thread_MsgRxFromBle(0x200,DAT_004a1af8,6);
        return;
      }
      if (cVar1 != '9') {
        if (cVar1 == -0x52) {
          if (cVar4 != '\0') {
            return;
          }
          uVar3 = param_1[4];
          iVar11 = FUN_0043d0ce();
          if (iVar11 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004a1af4,DAT_004a1af0,DAT_004a148c,0x306,DAT_004a1afc,(char)uVar3);
          }
          iVar11 = FUN_0043d0ce();
          if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_004a1b00,DAT_004a1b00,(char)uVar3);
          }
          iVar11 = FUN_0043d0ce();
          if (iVar11 << 0x1e < 0) {
            FUN_0043d574(3,DAT_004a1af4,DAT_004a1af0,DAT_004a148c,0x307,DAT_004a1b04,DAT_004a1af8[5]
                         ,DAT_004a1af8[4],DAT_004a1af8[3]);
          }
          iVar11 = FUN_0043d0ce();
          if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
            compress_log_output(0xcc00000,DAT_004a1b08,DAT_004a1b08,DAT_004a1af8[5],DAT_004a1af8[4],
                                DAT_004a1af8[3]);
          }
          iVar11 = FUN_0043d0ce();
          if (iVar11 << 0x1e < 0) {
            FUN_0043d574(3,DAT_004a1af4,DAT_004a1af0,DAT_004a148c,0x308,DAT_004a1b0c,DAT_004a1af8[2]
                         ,DAT_004a1af8[1],*DAT_004a1af8);
          }
          iVar11 = FUN_0043d0ce();
          if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
            compress_log_output(0xcc00000,DAT_004a1b10,DAT_004a1b10,DAT_004a1af8[2],DAT_004a1af8[1],
                                *DAT_004a1af8);
          }
          FUN_0047b59c(1,DAT_004a1af8);
          AppMasterSecClearAddr();
          _masterConnect(1);
          return;
        }
        if (cVar1 == -0x51) {
          if (cVar4 == '\0') {
            return;
          }
          iVar11 = DmConnRole(cVar4);
          if (iVar11 != 0) {
            return;
          }
          uVar2 = param_1[4];
          iVar11 = FUN_0043d0ce();
          if (iVar11 << 0x1e < 0) {
            FUN_0043d574(3,DAT_004a1af4,DAT_004a1af0,DAT_004a148c,0x315,DAT_004a1b14,uVar2);
          }
          iVar11 = FUN_0043d0ce();
          if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
            compress_log_output(0xc400000,DAT_004a1b18,DAT_004a1b18,uVar2);
          }
          uVar5 = uVar2 >> 1;
          if (((byte)uVar2 >> 6 & 1) == 0) {
            if ((uVar5 & 1 & uVar2 >> 8 & 1) == 0) {
              if ((uVar5 & 1) != 0) {
                iVar11 = FUN_0043d0ce();
                if (iVar11 << 0x1e < 0) {
                  FUN_0043d574(3,DAT_004a1af4,DAT_004a1af0,DAT_004a148c,0x324,DAT_004a1b24);
                }
                iVar11 = FUN_0043d0ce();
                if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
                  compress_log_output(0xc000000,DAT_004a1b28,DAT_004a1b28);
                }
              }
            }
            else {
              _SetRingLinkState(3,DAT_004a1b20);
            }
          }
          else {
            _SetRingLinkState(6,DAT_004a1b1c);
          }
          if ((uVar5 & 1) == 0) {
            return;
          }
          if (cVar4 == '\0') {
            return;
          }
          iVar11 = FUN_0043d0ce();
          if (iVar11 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004a1af4,DAT_004a1af0,DAT_004a148c,0x328,DAT_004a1b2c);
          }
          iVar11 = FUN_0043d0ce();
          if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_004a1b30,DAT_004a1b30);
          }
          FUN_004bb04a(cVar4);
          return;
        }
        if (cVar1 == -0x50) {
          if (cVar4 == '\0') {
            return;
          }
          iVar11 = FUN_0043d0ce();
          if (iVar11 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004a1af4,DAT_004a1af0,DAT_004a148c,0x334,DAT_004a1b34,cVar4);
          }
          iVar11 = FUN_0043d0ce();
          if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_004a1b38,DAT_004a1b38,cVar4);
          }
          _SetRingLinkState(5,DAT_004a1b3c);
          FUN_004bb04a(cVar4);
          return;
        }
        if (cVar1 == -0x4f) {
          iVar12 = *(int *)(param_1 + 2);
          FUN_0043dacc(DAT_004a1b40,0x10,iVar12,6);
          iVar11 = FUN_0043d0ce();
          if (iVar11 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004a1af4,DAT_004a1af0,DAT_004a148c,0x33f,DAT_004a1b44,
                         *(undefined1 *)(iVar12 + 6));
          }
          iVar11 = FUN_0043d0ce();
          if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_004a1b48,DAT_004a1b48,*(undefined1 *)(iVar12 + 6));
          }
          FUN_0047b59c(*(undefined1 *)(iVar12 + 6),iVar12);
          AppMasterSecClearAddr();
          iVar11 = FUN_00466010();
          FUN_0043c0e4(iVar11 + 0xc,6,0xff);
          FUN_004661a6();
          return;
        }
        if (cVar1 != -0x4e) {
          if (cVar1 == -0x4d) {
            if (*(char *)(*DAT_004a1b54 + 0x55) == '\0') {
              return;
            }
            iVar11 = DmConnRole(*(undefined1 *)(*DAT_004a1b54 + 0x55));
            if (iVar11 != 0) {
              return;
            }
            iVar11 = FUN_0043d0ce();
            if (iVar11 << 0x1e < 0) {
              FUN_0043d574(4,DAT_004a1af4,DAT_004a1af0,DAT_004a148c,0x353,DAT_004a1b58,
                           *(undefined1 *)(*piVar7 + 0x55));
            }
            iVar11 = FUN_0043d0ce();
            if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
              compress_log_output(0x10400000,DAT_004a1b5c,DAT_004a1b5c,
                                  *(undefined1 *)(*piVar7 + 0x55));
            }
            DmConnReadRssi(*(undefined1 *)(*piVar7 + 0x55));
            return;
          }
          if (cVar1 != -0x4c) {
            return;
          }
          if (*(char *)(*DAT_004a1b54 + 0x55) == '\0') {
            return;
          }
          iVar11 = DmConnRole(*(undefined1 *)(*DAT_004a1b54 + 0x55));
          if (iVar11 != 0) {
            return;
          }
          iVar11 = FUN_0043d0ce();
          if (iVar11 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004a1af4,DAT_004a1af0,DAT_004a1f34,0x35f,DAT_004a1f30,
                         *(undefined1 *)(*piVar7 + 0x55));
          }
          iVar11 = FUN_0043d0ce();
          if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_004a21bc,DAT_004a21bc,*(undefined1 *)(*piVar7 + 0x55)
                               );
          }
          FUN_00472596(*(undefined1 *)(*piVar7 + 0x55));
          return;
        }
        if (cVar4 == '\0') {
          return;
        }
        iVar11 = DmConnRole(cVar4);
        if (iVar11 != 0) {
          return;
        }
        uVar3 = param_1[4];
        iVar11 = FUN_0043d0ce();
        uVar8 = (undefined1)uVar3;
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004a1af4,DAT_004a1af0,DAT_004a148c,0x34b,DAT_004a1b4c,uVar8);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_004a1b50,DAT_004a1b50,uVar8);
        }
        _masterScan(uVar8);
        return;
      }
      if (cVar4 == '\0') {
        return;
      }
      iVar11 = DmConnRole(cVar4);
      if (iVar11 != 0) {
        return;
      }
      if (*(char *)((int)param_1 + 3) != '\0') {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(2,DAT_004a0fd0,DAT_004a0fcc,DAT_004a148c,0x2f9,DAT_004a19e4,
                       *(undefined1 *)((int)param_1 + 3));
        }
        iVar11 = FUN_0043d0ce();
        if ((-1 < iVar11 << 0x1f) && (iVar11 = FUN_0043d0ce(), -1 < iVar11 << 0x1d)) {
          return;
        }
        compress_log_output(0x8400000,DAT_004a19e8,DAT_004a19e8,*(undefined1 *)((int)param_1 + 3));
        return;
      }
      cVar1 = *(char *)(param_1 + 4);
      pbVar10 = (byte *)DmConnPeerAddr(cVar4);
      iVar11 = FUN_0043d0ce();
      if (iVar11 << 0x1e < 0) {
        local_20 = (uint)*pbVar10;
        local_24 = (uint)pbVar10[1];
        local_28 = (uint)pbVar10[2];
        local_2c = (uint)pbVar10[3];
        FUN_0043d574(3,DAT_004a0fd0,DAT_004a0fcc,DAT_004a148c,0x2f7,DAT_004a19dc,(int)cVar1,
                     pbVar10[5],pbVar10[4]);
      }
      iVar11 = FUN_0043d0ce();
      if ((-1 < iVar11 << 0x1f) && (iVar11 = FUN_0043d0ce(), -1 < iVar11 << 0x1d)) {
        return;
      }
      local_2c = (uint)*pbVar10;
      compress_log_output(0xdc00000,DAT_004a19e0,DAT_004a19e0,(int)cVar1,pbVar10[5],pbVar10[4],
                          pbVar10[3],pbVar10[2],pbVar10[1]);
      return;
    }
  }
  if ((cVar4 != '\0') && (iVar11 = DmConnRole(cVar4), iVar11 == 0)) {
    dmDiscCancel(param_1);
  }
  return;
}

