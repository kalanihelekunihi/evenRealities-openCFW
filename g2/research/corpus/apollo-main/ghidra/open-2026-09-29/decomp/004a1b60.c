
void APP_MasterConnectEvent(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  undefined4 uVar2;
  int *piVar3;
  char cVar4;
  int iVar5;
  ushort *puVar6;
  uint uVar7;
  uint uVar8;
  
  fw_event_loop_remove_delayed(DAT_004a23a8);
  *DAT_004a2364 = 0;
  uVar7 = (param_1 & 0xff) >> 7;
  uVar8 = (param_1 & 0xffff) >> 8 & 1;
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004a1fc0,DAT_004a1fbc,DAT_004a26b4,0x404,DAT_004a264c,param_1 & 0xfe7f,uVar7,
                 uVar8,*(undefined1 *)(*DAT_004a2648 + 0x55),param_4);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0x11000000,DAT_004a2650,DAT_004a2650,param_1 & 0xfe7f,uVar7,uVar8,
                        *(undefined1 *)(*DAT_004a2648 + 0x55));
  }
  piVar3 = DAT_004a2648;
  puVar1 = DAT_004a2058;
  if ((int)(param_1 << 0x1f) < 0) {
    *DAT_004a2058 = (char)uVar7;
    iVar5 = central_is_ring_owner_side_004a2914();
    if (iVar5 == 0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(2,DAT_004a1fc0,DAT_004a1fbc,DAT_004a26b4,0x40d,DAT_004a2654);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_004a26bc);
      }
      APP_MasterResetRetryConnectCnt();
      APP_MasterClearRingConnectFailureNotifyAfterRetry();
      *puVar1 = 0;
    }
    else if (*DAT_004a26c0 == '\x06') {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(3,DAT_004a1fc0,DAT_004a1fbc,DAT_004a26b4,0x416,DAT_004a26c4);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004a26c8,DAT_004a26c8);
      }
      APP_MasterClearRingConnectFailureNotifyAfterRetry();
      *puVar1 = 0;
    }
    else if ((uVar7 == 0) &&
            (iVar5 = central_master_link_matches_target_004a2864(DAT_004a26cc), iVar5 != 0)) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(3,DAT_004a1fc0,DAT_004a1fbc,DAT_004a26b4,0x421,DAT_004a26d0);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004a26d4,DAT_004a26d4);
      }
      APP_MasterClearRingConnectFailureNotifyAfterRetry();
      *puVar1 = 0;
      uVar2 = DAT_004a2360;
      fw_event_loop_remove_delayed(DAT_004a2360);
      fw_event_loop_push_delayed(uVar2,0,100);
      fw_event_loop_push_delayed(uVar2,0,2000);
      uVar2 = DAT_004a26d8;
      fw_event_loop_remove_delayed(DAT_004a26d8);
      fw_event_loop_push_delayed(uVar2,0,200);
    }
    else {
      piVar3 = DAT_004a2648;
      if ((*(char *)(*DAT_004a2648 + 0x55) != '\0') &&
         ((uVar7 == 0 && (cVar4 = DmConnRole(*(undefined1 *)(*DAT_004a2648 + 0x55)), cVar4 == '\0'))
         )) {
        iVar5 = DmConnPeerAddr(*(undefined1 *)(*piVar3 + 0x55));
        if ((iVar5 != 0) && (iVar5 = FUN_004d294a(iVar5,DAT_004a26cc), iVar5 != 0)) {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(3,DAT_004a1fc0,DAT_004a1fbc,DAT_004a26b4,0x432,DAT_004a26dc);
          }
          iVar5 = FUN_0043d0ce();
          if ((-1 < iVar5 << 0x1f) && (iVar5 = FUN_0043d0ce(), -1 < iVar5 << 0x1d)) {
            return;
          }
          compress_log_output(0xc000000,DAT_004a26e0,DAT_004a26e0);
          return;
        }
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004a1fc0,DAT_004a1fbc,DAT_004a26b4,0x436,DAT_004a26e4,
                       *(undefined1 *)(*piVar3 + 0x55));
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_004a2850,DAT_004a2850,*(undefined1 *)(*piVar3 + 0x55));
        }
        uVar2 = DAT_004a2854;
        fw_event_loop_remove_delayed(DAT_004a2854);
        fw_event_loop_push_delayed(uVar2,*(undefined1 *)(*piVar3 + 0x55),0);
      }
      puVar6 = (ushort *)WsfMsgAlloc(0xc);
      if (puVar6 != (ushort *)0x0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004a1fc0,DAT_004a1fbc,DAT_004a26b4,0x43e,DAT_004a2858);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004a28cc,DAT_004a28cc);
        }
        *(undefined1 *)(puVar6 + 1) = 0xae;
        *puVar6 = (ushort)*(byte *)(*piVar3 + 0x55);
        puVar6[4] = 1;
        WsfMsgSend(*(undefined1 *)(*piVar3 + 0x56),puVar6);
      }
    }
  }
  else if (((int)(param_1 << 0x1e) < 0) && (*(char *)(*DAT_004a2648 + 0x55) != '\0')) {
    *DAT_004a2058 = 0;
    puVar6 = (ushort *)WsfMsgAlloc(0xc);
    if (puVar6 != (ushort *)0x0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004a1fc0,DAT_004a1fbc,DAT_004a26b4,0x449,DAT_004a28d0);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004a28d4,DAT_004a28d4);
      }
      *(undefined1 *)(puVar6 + 1) = 0xaf;
      *puVar6 = (ushort)*(byte *)(*piVar3 + 0x55);
      puVar6[4] = (ushort)param_1 & 0xff7f;
      WsfMsgSend(*(undefined1 *)(*piVar3 + 0x56),puVar6);
    }
  }
  return;
}

