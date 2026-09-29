
void _exportFileParse(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  char *pcVar2;
  undefined1 *puVar3;
  int *piVar4;
  undefined1 uVar5;
  undefined4 uVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  int iVar11;
  undefined1 auStack_34 [4];
  undefined1 local_30;
  undefined1 local_2f;
  undefined1 local_2e;
  undefined1 local_2d;
  undefined1 local_2c;
  undefined1 local_2b;
  undefined1 local_2a;
  undefined1 local_29;
  undefined1 local_28;
  undefined1 local_27;
  undefined4 uStack_24;
  
  uStack_24 = param_4;
  FUN_0043c0e4(auStack_34,2,0);
  piVar1 = DAT_00448858;
  iVar9 = -1;
  if (param_1 == 0) {
    iVar8 = osKernelGetTickCount(0);
    *piVar1 = iVar8;
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004487a4,DAT_0044877c,DAT_00448860,0x6ba,DAT_0044885c,*piVar1);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00448864,DAT_00448864,*piVar1);
    }
    pcVar2 = DAT_00448868;
    if (*DAT_00448868 == '\0') {
      fw_event_loop_remove_delayed(DAT_0044886c);
      APP_ConnectParamOTASetFastMode();
    }
    piVar1 = DAT_00448660;
    if ((char)DAT_00448660[1] == '\x01') {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(2,DAT_004487a4,DAT_0044877c,DAT_00448860,0x6c2,DAT_00448870);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_00448874,DAT_00448874);
      }
      if (*piVar1 == 0) {
        iVar8 = 0;
      }
      else {
        iVar8 = file_close(*piVar1);
        *piVar1 = 0;
      }
      if (iVar8 < 0) {
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004487a4,DAT_0044877c,DAT_00448860,0x6c5,DAT_004487d4,(int)piVar1 + 5,
                       iVar8);
        }
        iVar9 = FUN_0043d0ce();
        if ((-1 < iVar9 << 0x1f) && (iVar9 = FUN_0043d0ce(), -1 < iVar9 << 0x1d)) {
          return;
        }
        compress_log_output(0x4800000,DAT_004487d8,DAT_004487d8,(int)piVar1 + 5,iVar8);
        return;
      }
    }
    FUN_0043c0e4(piVar1,0x70,0);
    puVar3 = DAT_00448878;
    FUN_0043c0e4(DAT_00448878,0x60,0);
    *puVar3 = 0;
    *(undefined4 *)(puVar3 + 0x34) = DAT_0044887c;
    iVar11 = (int)piVar1 + 5;
    FUN_00439be4(iVar11,param_2,param_3);
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004487a4,DAT_0044877c,DAT_00448860,0x6d1,DAT_00448880,iVar11);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00448884,DAT_00448884,iVar11);
    }
    iVar8 = _fileCaculateCRC(piVar1,iVar11,piVar1 + 0x16,piVar1 + 0x17);
    if (iVar8 == 0) {
      _evenOtaReplyToAPP(0xc2,0,3);
    }
    else {
      FUN_0043c0e4(&local_30,10,0);
      local_30 = 0;
      local_2f = 0;
      local_2e = (undefined1)piVar1[0x16];
      local_2d = (undefined1)((uint)piVar1[0x16] >> 8);
      local_2c = (undefined1)((uint)piVar1[0x16] >> 0x10);
      local_2b = (undefined1)((uint)piVar1[0x16] >> 0x18);
      local_2a = (undefined1)piVar1[0x17];
      local_29 = (undefined1)((uint)piVar1[0x17] >> 8);
      local_28 = (undefined1)((uint)piVar1[0x17] >> 0x10);
      local_27 = (undefined1)((uint)piVar1[0x17] >> 0x18);
      piVar1[0x1a] = piVar1[0x16];
      if (*pcVar2 == '\0') {
        Thread_MsgTransport3TxByBle(1,0xc2,&local_30,10);
      }
      uVar6 = semantic_OtaSelectFlashOps(1);
      iVar8 = file_open(iVar11,uVar6);
      *piVar1 = iVar8;
      if (*piVar1 == 0) {
        *(undefined1 *)(piVar1 + 1) = 0;
      }
      else {
        iVar9 = 0;
        *(undefined1 *)(piVar1 + 1) = 1;
      }
      if (iVar9 < 0) {
        iVar8 = FUN_0043d0ce();
        if (iVar8 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004487a4,DAT_0044877c,DAT_00448860,0x6ed,DAT_00448664,iVar11,iVar9);
        }
        iVar8 = FUN_0043d0ce();
        if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_004486e4,DAT_004486e4,iVar11,iVar9);
        }
      }
      else {
        *(undefined1 *)((int)piVar1 + 0x6d) = 1;
      }
    }
  }
  else {
    if (param_1 == 2) {
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004487a4,DAT_0044877c,DAT_00448860,0x6f5,DAT_00448888,DAT_00448660[0x19])
        ;
      }
      iVar9 = FUN_0043d0ce();
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0044888c,DAT_0044888c,DAT_00448660[0x19]);
      }
      piVar1 = DAT_00448660;
      if ((uint)DAT_00448660[0x19] < 0x1000) {
        DAT_00448660[0x19] = 0;
        file_seek(*piVar1,piVar1[0x19],0);
      }
      else {
        DAT_00448660[0x19] = DAT_00448660[0x19] - DAT_00448660[0x18];
        file_seek(*piVar1,piVar1[0x19],0);
      }
    }
    else if (1 < param_1) {
      if (param_1 != 3) {
        return;
      }
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004487a4,DAT_0044877c,DAT_00448860,0x740,DAT_004488c8);
      }
      iVar9 = FUN_0043d0ce();
      if ((-1 < iVar9 << 0x1f) && (iVar9 = FUN_0043d0ce(), -1 < iVar9 << 0x1d)) {
        return;
      }
      compress_log_output(0x10000000,DAT_004488cc,DAT_004488cc);
      return;
    }
    piVar1 = DAT_00448660;
    if (*(char *)((int)DAT_00448660 + 0x6d) != '\0') {
      uVar6 = osKernelGetTickCount();
      *DAT_00448890 = uVar6;
      uVar6 = DAT_0044887c;
      uVar10 = 0x1000;
      FUN_0043c0e4(DAT_0044887c,0x1000,0);
      if ((uint)piVar1[0x1a] < 0x1000) {
        uVar10 = piVar1[0x1a];
      }
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004487a4,DAT_0044877c,DAT_00448860,0x70b,DAT_00448894,uVar10,piVar1[0x1a]
                    );
      }
      iVar9 = FUN_0043d0ce();
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_00448898,DAT_00448898,uVar10,piVar1[0x1a]);
      }
      uVar7 = file_read(uVar6,1,uVar10,*piVar1);
      if (uVar7 == uVar10) {
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004487a4,DAT_0044877c,DAT_00448860,0x716,DAT_004488a4,uVar7);
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_004488a8,DAT_004488a8,uVar7);
        }
        piVar1[0x19] = uVar7 + piVar1[0x19];
        piVar1[0x18] = uVar7;
        piVar1[0x1a] = piVar1[0x16] - piVar1[0x19];
        pcVar2 = DAT_00448868;
        if (*DAT_00448868 == '\0') {
          Thread_MsgTransport3TxByBle(1,0xc3,uVar6,uVar7 & 0xffff);
        }
        _evenOtaReplyToAPP(0xc2,1,0);
        if (piVar1[0x16] != 0) {
          uVar5 = FUN_0047cc60((int)((ulonglong)(uint)piVar1[0x19] * 100),
                               (int)((ulonglong)(uint)piVar1[0x19] * 100 >> 0x20),piVar1[0x16],0);
          *(undefined1 *)(piVar1 + 0x1b) = uVar5;
        }
        piVar4 = DAT_004488ac;
        iVar9 = osKernelGetTickCount();
        *piVar4 = iVar9;
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004487a4,DAT_0044877c,DAT_00448860,0x726,DAT_004488b0,
                       (char)piVar1[0x1b],*piVar4 - *DAT_00448858,
                       ((uint)(piVar1[0x19] * 1000) >> 10) / (uint)(*piVar4 - *DAT_00448858));
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0x10c00000,DAT_004488b4,DAT_004488b4,(char)piVar1[0x1b],
                              *piVar4 - *DAT_00448858,
                              ((uint)(piVar1[0x19] * 1000) >> 10) / (uint)(*piVar4 - *DAT_00448858))
          ;
        }
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004487a4,DAT_0044877c,DAT_00448860,0x729,DAT_004488b8,piVar1[0x19],
                       piVar1[0x16],piVar1[0x17]);
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0x10c00000,DAT_004488bc,DAT_004488bc,piVar1[0x19],piVar1[0x16],
                              piVar1[0x17]);
        }
        if ((uint)piVar1[0x16] <= (uint)piVar1[0x19]) {
          *(undefined1 *)((int)piVar1 + 0x6d) = 0;
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(3,DAT_004487a4,DAT_0044877c,DAT_00448860,0x72c,DAT_004488c0,(int)piVar1 + 5
                        );
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0xc400000,DAT_004488c4,DAT_004488c4,(int)piVar1 + 5);
          }
          if (*piVar1 == 0) {
            iVar9 = 0;
          }
          else {
            iVar9 = file_close(*piVar1);
            *piVar1 = 0;
          }
          if (iVar9 < 0) {
            iVar8 = FUN_0043d0ce();
            if (iVar8 << 0x1e < 0) {
              FUN_0043d574(1,DAT_004487a4,DAT_0044877c,DAT_00448860,0x72f,DAT_004487d4,
                           (int)piVar1 + 5,iVar9);
            }
            iVar8 = FUN_0043d0ce();
            if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
              compress_log_output(0x4800000,DAT_004487d8,DAT_004487d8,(int)piVar1 + 5,iVar9);
            }
            _evenOtaReplyToAPP(0xc2,1,10);
          }
          else {
            *(undefined1 *)(piVar1 + 1) = 0;
            FUN_0043c0e4(piVar1,0x70,0);
            _evenOtaReplyToAPP(0xc2,3,0);
            if (*pcVar2 == '\0') {
              ble_param_reset_delayed_event(2000);
            }
          }
        }
      }
      else {
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004487a4,DAT_0044877c,DAT_00448860,0x70e,DAT_0044889c,uVar7);
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_004488a0,DAT_004488a0,uVar7);
        }
        if (*piVar1 == 0) {
          iVar9 = 0;
        }
        else {
          iVar9 = file_close(*piVar1);
          *piVar1 = 0;
        }
        if (iVar9 < 0) {
          iVar8 = FUN_0043d0ce();
          if (iVar8 << 0x1e < 0) {
            FUN_0043d574(1,DAT_004487a4,DAT_0044877c,DAT_00448860,0x711,DAT_004487d4,(int)piVar1 + 5
                         ,iVar9);
          }
          iVar8 = FUN_0043d0ce();
          if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_004487d8,DAT_004487d8,(int)piVar1 + 5,iVar9);
          }
          _evenOtaReplyToAPP(0xc2,1,10);
        }
      }
    }
  }
  return;
}

