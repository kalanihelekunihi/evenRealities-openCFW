
void _fileCmdParse(byte param_1,int param_2,int param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int *piVar2;
  undefined1 *puVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int *piVar7;
  char cVar8;
  int iVar9;
  int iVar10;
  undefined4 uVar11;
  uint uVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  undefined1 auStack_24 [4];
  undefined4 uStack_20;
  
  uStack_20 = param_4;
  FUN_0043c0e4(auStack_24,2,0);
  puVar1 = DAT_00446364;
  iVar14 = -1;
  if (param_1 == 0) {
    uVar11 = osKernelGetTickCount(0);
    *puVar1 = uVar11;
    _RPC_SystemOtaStatusSync(1);
    iVar14 = FUN_0043d0ce();
    if (iVar14 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x40b,DAT_00446368,*puVar1);
    }
    iVar14 = FUN_0043d0ce();
    if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00446390,DAT_00446390,*puVar1);
    }
    if (*DAT_00446394 == '\0') {
      fw_event_loop_remove_delayed(DAT_00446398);
      APP_ConnectParamOTASetFastMode();
      fw_event_loop_remove_delayed(DAT_0044639c);
    }
    piVar2 = DAT_004463a0;
    if ((char)DAT_004463a0[1] == '\x01') {
      iVar14 = FUN_0043d0ce();
      if (iVar14 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0044638c,DAT_00446388,DAT_00446384,0x413,DAT_004463a4);
      }
      iVar14 = FUN_0043d0ce();
      if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_004463a8,DAT_004463a8);
      }
      if (*piVar2 == 0) {
        iVar14 = 0;
      }
      else {
        iVar14 = file_close(*piVar2);
        *piVar2 = 0;
      }
      if (iVar14 < 0) {
        iVar13 = FUN_0043d0ce();
        if (iVar13 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0044638c,DAT_00446388,DAT_00446384,0x416,DAT_004463ac,(int)piVar2 + 5,
                       iVar14);
        }
        iVar13 = FUN_0043d0ce();
        if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_004463b0,DAT_004463b0,(int)piVar2 + 5,iVar14);
        }
        _evenOtaReplyToAPP(0xc0,0,10);
        return;
      }
    }
    FUN_0043c0e4(piVar2,0x70,0);
    puVar3 = DAT_004463b4;
    FUN_0043c0e4(DAT_004463b4,0x60,0);
    iVar14 = _otaFsHealthCheckAndHeal();
    if (iVar14 != 0) {
      iVar14 = FUN_0043d0ce();
      if (iVar14 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0044638c,DAT_00446388,DAT_00446384,0x421,DAT_004463b8);
      }
      iVar14 = FUN_0043d0ce();
      if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004463bc,DAT_004463bc);
      }
      _evenOtaReplyToAPP(0xc0,0,10);
      return;
    }
    *puVar3 = 0;
    *(undefined4 *)(puVar3 + 0x34) = DAT_004463c0;
    _evenOtaReplyToAPP(0xc0,0,0);
    return;
  }
  if (param_1 == 2) {
    *(undefined1 *)((int)DAT_004463a0 + 0x6d) = 1;
    uVar11 = osKernelGetTickCount();
    *DAT_00446ca8 = uVar11;
    return;
  }
  if (1 < param_1) {
    if (param_1 != 3) {
      return;
    }
    iVar14 = FUN_0043d0ce();
    if (iVar14 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00446cb8,DAT_00446cb4,DAT_00446cb0,0x4cf,DAT_00446cac);
    }
    iVar14 = FUN_0043d0ce();
    if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00446cbc,DAT_00446cbc);
    }
    iVar14 = FUN_0043d0ce();
    if (iVar14 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00446cb8,DAT_00446cb4,DAT_00446cb0,0x4d0,DAT_00446cc4,DAT_00446cc0[0x17],
                   *(undefined4 *)(DAT_00447114 + 0x10));
    }
    iVar14 = FUN_0043d0ce();
    if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_00446cc8,DAT_00446cc8,DAT_00446cc0[0x17],
                          *(undefined4 *)(DAT_00447114 + 0x10));
    }
    puVar3 = DAT_00447114;
    uVar12 = *(uint *)(DAT_00447114 + 0x28);
    if (uVar12 == 0) {
      iVar14 = FUN_0043d0ce();
      if (iVar14 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00446cb8,DAT_00446cb4,DAT_00446cb0,0x4d3,DAT_004471b0);
      }
      iVar14 = FUN_0043d0ce();
      if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00447210,DAT_00447210);
      }
      piVar2 = DAT_00446cc0;
      if (*(int *)(puVar3 + 0x2c) == 0) {
        if (DAT_00446cc0[0x17] == *(int *)(puVar3 + 0x10)) {
          _evenOtaReplyToAPP(0xc0,3,8);
          iVar14 = FUN_0043d0ce();
          if (iVar14 << 0x1e < 0) {
            FUN_0043d574(4,DAT_00446cb8,DAT_00446cb4,DAT_00446cb0,0x4d8,DAT_00446ccc);
          }
          iVar14 = FUN_0043d0ce();
          if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_00446cd0,DAT_00446cd0);
          }
          *DAT_00446cd4 = 0;
          semantic_OtaCommitDescriptor();
          uVar11 = DAT_00446cdc;
          if (*DAT_00446cd8 == '\0') {
            fw_event_loop_remove_delayed(DAT_00446cdc);
            fw_event_loop_push_delayed(uVar11,0,3000);
          }
          _evenOtaReplyToAPP(0xc0,4,9);
        }
        else {
          iVar14 = FUN_0043d0ce();
          if (iVar14 << 0x1e < 0) {
            FUN_0043d574(1,DAT_00446cb8,DAT_00446cb4,DAT_00446cb0,0x4e3,DAT_00446ce0);
          }
          iVar14 = FUN_0043d0ce();
          if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_00446ce4,DAT_00446ce4);
          }
          *DAT_00446cd4 = 1;
          _evenOtaReplyToAPP(0xc0,3,7);
        }
        piVar7 = DAT_00446ce8;
        if (*(int *)(*DAT_00446ce8 + 0xc) != 0) {
          (**(code **)(*DAT_00446ce8 + 0xc))();
        }
        *puVar3 = 0;
        piVar2[0x17] = 0;
        *piVar7 = DAT_00446cec;
      }
      else if (*(int *)(puVar3 + 0x2c) == 1) {
        iVar14 = FUN_0043d0ce();
        if (iVar14 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00446cb8,DAT_00446cb4,DAT_00446cb0,0x4ee,DAT_00446cf0,
                       DAT_00446cc0[0x17],*(undefined4 *)(puVar3 + 0x10));
        }
        iVar14 = FUN_0043d0ce();
        if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_00446cf4,DAT_00446cf4,DAT_00446cc0[0x17],
                              *(undefined4 *)(puVar3 + 0x10));
        }
        piVar2 = DAT_00446cc0;
        if (DAT_00446cc0[0x17] == *(int *)(puVar3 + 0x10)) {
          _evenOtaReplyToAPP(0xc0,3,8);
          iVar14 = FUN_0043d0ce();
          if (iVar14 << 0x1e < 0) {
            FUN_0043d574(4,DAT_00446cb8,DAT_00446cb4,DAT_00446cb0,0x4f2,DAT_00446cf8);
          }
          iVar14 = FUN_0043d0ce();
          if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_00446cfc,DAT_00446cfc);
          }
          *DAT_00446cd4 = 0;
          _evenOtaReplyToAPP(0xc0,4,9);
        }
        else {
          iVar14 = FUN_0043d0ce();
          if (iVar14 << 0x1e < 0) {
            FUN_0043d574(1,DAT_00446cb8,DAT_00446cb4,DAT_00446cb0,0x4f6,DAT_00446d00);
          }
          iVar14 = FUN_0043d0ce();
          if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_00446d04,DAT_00446d04);
          }
          *DAT_00446cd4 = 1;
          _evenOtaReplyToAPP(0xc0,3,7);
        }
        *puVar3 = 0;
        piVar2[0x17] = 0;
      }
    }
    else if (uVar12 == 2) {
      iVar14 = FUN_0043d0ce();
      if (iVar14 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00446cb8,DAT_00446cb4,DAT_00446cb0,0x507,DAT_004474bc);
      }
      iVar14 = FUN_0043d0ce();
      if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004474c0,DAT_004474c0);
      }
    }
    else if (uVar12 < 2) {
      iVar14 = FUN_0043d0ce();
      if (iVar14 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00446cb8,DAT_00446cb4,DAT_00446cb0,0x502,DAT_004474b4);
      }
      iVar14 = FUN_0043d0ce();
      if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004474b8,DAT_004474b8);
      }
    }
    else if (uVar12 == 4) {
      iVar14 = FUN_0043d0ce();
      if (iVar14 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00446cb8,DAT_00446cb4,DAT_00446cb0,0x511,DAT_00447558);
      }
      iVar14 = FUN_0043d0ce();
      if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_0044755c,DAT_0044755c);
      }
    }
    else if (uVar12 < 4) {
      iVar14 = FUN_0043d0ce();
      if (iVar14 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00446cb8,DAT_00446cb4,DAT_00446cb0,0x50c,DAT_00447550);
      }
      iVar14 = FUN_0043d0ce();
      if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00447554,DAT_00447554);
      }
    }
    else if (uVar12 == 6) {
      iVar14 = FUN_0043d0ce();
      if (iVar14 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00446cb8,DAT_00446cb4,DAT_00446cb0,0x51b,DAT_00446d08);
      }
      iVar14 = FUN_0043d0ce();
      if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00446d0c,DAT_00446d0c);
      }
    }
    else if (uVar12 < 6) {
      iVar14 = FUN_0043d0ce();
      if (iVar14 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00446cb8,DAT_00446cb4,DAT_00446cb0,0x516,DAT_00447560);
      }
      iVar14 = FUN_0043d0ce();
      if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00447564,DAT_00447564);
      }
    }
    iVar14 = DAT_0044786c;
    piVar2 = DAT_00446cc0;
    if (*(int *)(puVar3 + 0x2c) != 3) {
      if (*(int *)(puVar3 + 0x2c) != 1) {
        return;
      }
      if (*(int *)(DAT_0044786c + 0x5c) == *(int *)(puVar3 + 0x10)) {
        *DAT_00446cd4 = 0;
        iVar13 = FUN_0043d0ce();
        if (iVar13 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00446cb8,DAT_00446cb4,DAT_00446cb0,0x555,DAT_00446d30);
        }
        iVar13 = FUN_0043d0ce();
        if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_00446d34,DAT_00446d34);
        }
        _evenOtaReplyToAPP(0xc0,3,8);
      }
      else {
        *DAT_00446cd4 = 1;
        iVar13 = FUN_0043d0ce();
        if (iVar13 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00446cb8,DAT_00446cb4,DAT_00446cb0,0x55a,DAT_00446d38);
        }
        iVar13 = FUN_0043d0ce();
        if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_00446d3c,DAT_00446d3c);
        }
        _evenOtaReplyToAPP(0xc0,3,7);
      }
      FUN_0043c0e4(iVar14,0x70,0);
      *(undefined4 *)(puVar3 + 0x3c) = 0;
      *(undefined4 *)(iVar14 + 100) = 0;
      return;
    }
    if ((char)DAT_00446cc0[1] != '\x01') {
      iVar14 = FUN_0043d0ce();
      if (iVar14 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00446cb8,DAT_00446cb4,DAT_00446cb0,0x52d,DAT_00446d20,(int)piVar2 + 5);
      }
      iVar14 = FUN_0043d0ce();
      if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00446d24,DAT_00446d24,(int)piVar2 + 5);
      }
      _evenOtaReplyToAPP(0xc0,3,7);
      return;
    }
    if (*DAT_00446cc0 == 0) {
      iVar14 = 0;
    }
    else {
      iVar14 = file_close(*DAT_00446cc0);
      *piVar2 = 0;
    }
    if (-1 < iVar14) {
      *(undefined1 *)(piVar2 + 1) = 0;
      iVar14 = FUN_0043d0ce();
      if (iVar14 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00446cb8,DAT_00446cb4,DAT_00446cb0,0x531,DAT_00446d18,
                     *(undefined4 *)(puVar3 + 0x3c),piVar2[0x19],piVar2[0x16]);
      }
      iVar14 = FUN_0043d0ce();
      if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
        compress_log_output(0x10c00000,DAT_00446d1c,DAT_00446d1c,*(undefined4 *)(puVar3 + 0x3c),
                            piVar2[0x19],piVar2[0x16]);
      }
      if (piVar2[0x17] == *(int *)(puVar3 + 0x10)) {
        *DAT_00446cd4 = 0;
        _evenOtaReplyToAPP(0xc0,3,8);
        if (*(int *)(puVar3 + 0x28) == 0) {
          FUN_00478860(0x55555555);
          _evenOtaReplyToAPP(0xc0,4,9);
          uVar11 = DAT_00446cdc;
          if (*DAT_00446cd8 == '\0') {
            fw_event_loop_remove_delayed(DAT_00446cdc);
            fw_event_loop_push_delayed(uVar11,0,3000);
          }
          _RPC_SystemOtaStatusSync(0);
        }
        else if ((*(int *)(puVar3 + 0x28) == 1) &&
                (iVar14 = _evenOtaBootloaderWriteFile2MRAM
                                    ((int)piVar2 + 5,*(undefined4 *)(puVar3 + 0x38)), iVar14 != 0))
        {
          iVar13 = FUN_0043d0ce();
          if (iVar13 << 0x1e < 0) {
            FUN_0043d574(1,DAT_00446cb8,DAT_00446cb4,DAT_00446cb0,0x544,DAT_00446d28,iVar14);
          }
          iVar13 = FUN_0043d0ce();
          if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
            compress_log_output(0x4400000,DAT_00446d2c,DAT_00446d2c,iVar14);
          }
          _evenOtaReplyToAPP(0xc0,3,7);
          return;
        }
      }
      else {
        *DAT_00446cd4 = 1;
        file_remove((int)piVar2 + 5);
        _evenOtaReplyToAPP(0xc0,3,7);
      }
      FUN_0043c0e4(piVar2,0x70,0);
      *(undefined4 *)(puVar3 + 0x3c) = 0;
      piVar2[0x19] = 0;
      return;
    }
    iVar13 = FUN_0043d0ce();
    if (iVar13 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00446cb8,DAT_00446cb4,DAT_00446cb0,0x527,DAT_00446d10,(int)piVar2 + 5,
                   iVar14);
    }
    iVar13 = FUN_0043d0ce();
    if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_00446d14,DAT_00446d14,(int)piVar2 + 5,iVar14);
    }
    _evenOtaReplyToAPP(0xc0,3,7);
    return;
  }
  iVar13 = FUN_0043d0ce();
  if (iVar13 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x430,DAT_004463c4,param_3);
  }
  iVar13 = FUN_0043d0ce();
  if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004463c8,DAT_004463c8,param_3);
  }
  piVar2 = DAT_004463a0;
  DAT_004463a0[0x19] = 0;
  if (param_3 != 0x80) {
    iVar14 = FUN_0043d0ce();
    if (iVar14 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x434,DAT_004463cc);
    }
    iVar14 = FUN_0043d0ce();
    if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004463d0,DAT_004463d0);
    }
    _evenOtaReplyToAPP(0xc0,1,1);
    return;
  }
  piVar2[0x17] = 0;
  puVar3 = DAT_004463b4;
  FUN_00439be4(DAT_004463b4 + 4,param_2,0x30);
  iVar15 = (int)piVar2 + 5;
  FUN_00439be4(iVar15,param_2 + 0x30,0x50);
  piVar2[0x16] = *(int *)(puVar3 + 0xc);
  iVar13 = FUN_0043d0ce();
  if (iVar13 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x441,DAT_00446600);
  }
  iVar13 = FUN_0043d0ce();
  if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_00446604,DAT_00446604);
  }
  iVar13 = FUN_0043d0ce();
  if (iVar13 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x442,DAT_00446608,
                 *(undefined4 *)(puVar3 + 4));
  }
  iVar13 = FUN_0043d0ce();
  if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0044660c,DAT_0044660c,*(undefined4 *)(puVar3 + 4));
  }
  iVar13 = FUN_0043d0ce();
  if (iVar13 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x443,DAT_00446610,
                 *(undefined4 *)(puVar3 + 0x24));
  }
  iVar13 = FUN_0043d0ce();
  if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00446614,DAT_00446614,*(undefined4 *)(puVar3 + 0x24));
  }
  iVar13 = FUN_0043d0ce();
  if (iVar13 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x444,DAT_00446618,
                 *(undefined4 *)(puVar3 + 0xc));
  }
  iVar13 = FUN_0043d0ce();
  if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0044661c,DAT_0044661c,*(undefined4 *)(puVar3 + 0xc));
  }
  iVar13 = FUN_0043d0ce();
  if (iVar13 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x445,DAT_00446620,
                 *(undefined4 *)(puVar3 + 0x10));
  }
  iVar13 = FUN_0043d0ce();
  if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00446624,DAT_00446624,*(undefined4 *)(puVar3 + 0x10));
  }
  iVar13 = FUN_0043d0ce();
  if (iVar13 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x446,DAT_00446628,
                 *(undefined4 *)(puVar3 + 8));
  }
  iVar13 = FUN_0043d0ce();
  if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0044662c,DAT_0044662c,*(undefined4 *)(puVar3 + 8));
  }
  iVar13 = FUN_0043d0ce();
  if (iVar13 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x447,DAT_00446630,
                 *(undefined4 *)(puVar3 + 0x28));
  }
  iVar13 = FUN_0043d0ce();
  if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00446634,DAT_00446634,*(undefined4 *)(puVar3 + 0x28));
  }
  iVar13 = FUN_0043d0ce();
  if (iVar13 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x448,DAT_00446638,
                 *(undefined4 *)(puVar3 + 0x2c));
  }
  iVar13 = FUN_0043d0ce();
  if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0044663c,DAT_0044663c,*(undefined4 *)(puVar3 + 0x2c));
  }
  iVar13 = FUN_0043d0ce();
  if (iVar13 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x449,DAT_00446640,
                 *(undefined4 *)(puVar3 + 0x30));
  }
  iVar13 = FUN_0043d0ce();
  if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00446644,DAT_00446644,*(undefined4 *)(puVar3 + 0x30));
  }
  iVar13 = FUN_0043d0ce();
  if (iVar13 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x44a,DAT_00446648,iVar15);
  }
  iVar13 = FUN_0043d0ce();
  if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0044664c,DAT_0044664c,iVar15);
  }
  iVar13 = FUN_0043d0ce();
  if (iVar13 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,1099,DAT_00446650);
  }
  iVar13 = FUN_0043d0ce();
  if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_00446654,DAT_00446654);
  }
  iVar6 = DAT_00446b5c;
  iVar5 = DAT_00446b50;
  iVar4 = DAT_00446b44;
  iVar9 = DAT_00446ad8;
  iVar10 = DAT_004469cc;
  iVar13 = DAT_00446954;
  uVar12 = *(uint *)(puVar3 + 0x28);
  if (uVar12 == 0) {
    iVar10 = FUN_0043d0ce();
    if (iVar10 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x451,DAT_00446958,iVar13);
    }
    iVar10 = FUN_0043d0ce();
    if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004469bc,DAT_004469bc,iVar13);
    }
    *(undefined4 *)(puVar3 + 0x38) = 0;
    *(undefined4 *)(puVar3 + 0x3c) = 0;
    piVar2[0x19] = 0;
    if (*(int *)(puVar3 + 0x2c) == 0) {
      *(undefined2 *)(DAT_004469c0 + 4) = 0;
      cVar8 = _evenOtaSetFwAddr();
      iVar10 = FUN_0043d0ce();
      if (iVar10 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x458,DAT_004469c4,
                     *(undefined4 *)(puVar3 + 0x38),cVar8);
      }
      iVar10 = FUN_0043d0ce();
      if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_004469c8,DAT_004469c8,*(undefined4 *)(puVar3 + 0x38),
                            cVar8);
      }
      if (cVar8 == '\0') {
        _evenOtaReplyToAPP(0xc0,1,1);
        *puVar3 = 0;
        return;
      }
    }
  }
  else {
    iVar13 = iVar15;
    if (uVar12 == 2) {
      _evenOtaSetFwAddr();
      iVar10 = FUN_0043d0ce();
      if (iVar10 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x46c,DAT_00446a84,iVar15);
      }
      iVar10 = FUN_0043d0ce();
      if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_00446ad4,DAT_00446ad4,iVar15);
      }
    }
    else if (uVar12 < 2) {
      _evenOtaSetFwAddr();
      iVar13 = FUN_0043d0ce();
      if (iVar13 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x465,DAT_004469d0,iVar10);
      }
      iVar9 = FUN_0043d0ce();
      iVar13 = iVar10;
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_00446a80,DAT_00446a80,iVar10);
      }
    }
    else if (uVar12 == 4) {
      iVar13 = FUN_0043d0ce();
      if (iVar13 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x478,DAT_00446b48,iVar4);
      }
      iVar10 = FUN_0043d0ce();
      iVar13 = iVar4;
      if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_00446b4c,DAT_00446b4c,iVar4);
      }
    }
    else if (uVar12 < 4) {
      iVar13 = FUN_0043d0ce();
      if (iVar13 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x472,DAT_00446adc,iVar9);
      }
      iVar10 = FUN_0043d0ce();
      iVar13 = iVar9;
      if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_00446ae0,DAT_00446ae0,iVar9);
      }
    }
    else if (uVar12 == 6) {
      iVar13 = FUN_0043d0ce();
      if (iVar13 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x484,DAT_00446bec,iVar6);
      }
      iVar10 = FUN_0043d0ce();
      iVar13 = iVar6;
      if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_00446bf0,DAT_00446bf0,iVar6);
      }
    }
    else if (uVar12 < 6) {
      iVar13 = FUN_0043d0ce();
      if (iVar13 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x47e,DAT_00446b54,iVar5);
      }
      iVar10 = FUN_0043d0ce();
      iVar13 = iVar5;
      if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_00446b58,DAT_00446b58,iVar5);
      }
    }
    else if (uVar12 == 7) {
      iVar10 = FUN_0043d0ce();
      if (iVar10 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x48a,DAT_00446bf4,iVar15);
      }
      iVar10 = FUN_0043d0ce();
      if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_00446c60,DAT_00446c60,iVar15);
      }
    }
    else {
      iVar10 = FUN_0043d0ce();
      if (iVar10 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x490,DAT_00446c64,iVar15);
      }
      iVar10 = FUN_0043d0ce();
      if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_00446c68,DAT_00446c68,iVar15);
      }
    }
  }
  if (*(int *)(puVar3 + 0x2c) == 3) {
    if (iVar13 != 0) {
      uVar11 = FUN_0044a43c(iVar13);
      iVar13 = FUN_0044b610(iVar15,iVar13,uVar11);
      if (iVar13 == 0) {
        iVar13 = FUN_0043d0ce();
        if (iVar13 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x496,DAT_00446c6c,iVar15);
        }
        iVar13 = FUN_0043d0ce();
        if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_00446c70,DAT_00446c70,iVar15);
        }
        iVar13 = file_remove(iVar15);
        if ((iVar13 < 0) && (iVar13 != -2)) {
          iVar10 = FUN_0043d0ce();
          if (iVar10 << 0x1e < 0) {
            FUN_0043d574(1,DAT_0044638c,DAT_00446388,DAT_00446384,0x49a,DAT_00446c74,iVar15,iVar13);
          }
          iVar10 = FUN_0043d0ce();
          if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_00446c78,DAT_00446c78,iVar15,iVar13);
          }
        }
        uVar11 = semantic_OtaSelectFlashOps(0x103);
        iVar13 = file_open(iVar15,uVar11);
        *piVar2 = iVar13;
        if (*piVar2 == 0) {
          iVar13 = -1;
          *(undefined1 *)(piVar2 + 1) = 0;
        }
        else {
          iVar13 = 0;
          *(undefined1 *)(piVar2 + 1) = 1;
        }
        if (iVar13 < 0) {
          iVar14 = FUN_0043d0ce();
          if (iVar14 << 0x1e < 0) {
            FUN_0043d574(1,DAT_0044638c,DAT_00446388,DAT_00446384,0x49e,DAT_00446c7c,iVar15,iVar13);
          }
          iVar14 = FUN_0043d0ce();
          if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_00446c80,DAT_00446c80,iVar15,iVar13);
          }
          _evenOtaReplyToAPP(0xc0,1,6);
          return;
        }
        if (*piVar2 == 0) {
          iVar13 = 0;
        }
        else {
          iVar13 = file_close(*piVar2);
          *piVar2 = 0;
        }
        if (iVar13 < 0) {
          iVar14 = FUN_0043d0ce();
          if (iVar14 << 0x1e < 0) {
            FUN_0043d574(1,DAT_0044638c,DAT_00446388,DAT_00446384,0x4a4,DAT_004463ac,iVar15,iVar13);
          }
          iVar14 = FUN_0043d0ce();
          if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_004463b0,DAT_004463b0,iVar15,iVar13);
          }
          _evenOtaReplyToAPP(0xc0,1,6);
          return;
        }
        uVar11 = semantic_OtaSelectFlashOps(3);
        iVar13 = file_open(iVar15,uVar11);
        *piVar2 = iVar13;
        if (*piVar2 == 0) {
          *(undefined1 *)(piVar2 + 1) = 0;
        }
        else {
          iVar14 = 0;
          *(undefined1 *)(piVar2 + 1) = 1;
        }
        if (iVar14 < 0) {
          iVar13 = FUN_0043d0ce();
          if (iVar13 << 0x1e < 0) {
            FUN_0043d574(1,DAT_0044638c,DAT_00446388,DAT_00446384,0x4ab,DAT_00446c7c,iVar15,iVar14);
          }
          iVar13 = FUN_0043d0ce();
          if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_00446c80,DAT_00446c80,iVar15,iVar14);
          }
          _evenOtaReplyToAPP(0xc0,1,6);
          return;
        }
        goto LAB_00446314;
      }
    }
    iVar14 = FUN_0043d0ce();
    if (iVar14 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0044638c,DAT_00446388,DAT_00446384,0x4b0,DAT_00446c84,iVar15);
    }
    iVar14 = FUN_0043d0ce();
    if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00446c88,DAT_00446c88,iVar15);
    }
    _evenOtaReplyToAPP(0xc0,1,1);
  }
  else {
    if (*(int *)(puVar3 + 0x2c) == 1) {
      uVar12 = semantic_OtaParseHexAddress(iVar15);
      if (DAT_00446c8c <= uVar12 + 0x80000000) {
        iVar14 = FUN_0043d0ce();
        if (iVar14 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0044638c,DAT_00446388,DAT_00446384,0x4b9,DAT_00446c90,iVar15);
        }
        iVar14 = FUN_0043d0ce();
        if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_00446c94,DAT_00446c94,iVar15);
        }
        _evenOtaReplyToAPP(0xc0,1,1);
        return;
      }
      *(uint *)(puVar3 + 0x38) = uVar12 & 0x7fffffff;
      iVar14 = FUN_0043d0ce();
      if (iVar14 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0044638c,DAT_00446388,DAT_00446384,0x4be,DAT_00446c98,uVar12,
                     *(undefined4 *)(puVar3 + 0x38));
      }
      iVar14 = FUN_0043d0ce();
      if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
        compress_log_output(0x8800000,DAT_00446c9c,DAT_00446c9c,uVar12,
                            *(undefined4 *)(puVar3 + 0x38));
      }
    }
LAB_00446314:
    *puVar3 = 1;
    iVar14 = FUN_0043d0ce();
    if (iVar14 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0044638c,DAT_00446388,DAT_00446384,0x4c2,DAT_00446ca0);
    }
    iVar14 = FUN_0043d0ce();
    if ((iVar14 << 0x1f < 0) || (iVar14 = FUN_0043d0ce(), iVar14 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00446ca4,DAT_00446ca4);
    }
    _evenOtaReplyToAPP(0xc0,1,0);
  }
  return;
}

