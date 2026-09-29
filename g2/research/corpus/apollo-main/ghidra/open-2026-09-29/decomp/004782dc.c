
void APP_ConnectParamHandler(undefined4 param_1,ushort *param_2)

{
  char cVar1;
  ushort uVar2;
  undefined1 uVar3;
  int *piVar4;
  int iVar5;
  int iVar6;
  
  if (param_2 != (ushort *)0x0) {
    iVar6 = 0;
    if ((*param_2 != 0) && (*param_2 < 4)) {
      iVar6 = DAT_00478740 + (uint)*param_2 * 0x30 + -0x30;
    }
    cVar1 = (char)param_2[1];
    if (cVar1 == '\'') {
      iVar6 = DmConnRole((char)*param_2);
      if (iVar6 == 1) {
        _bleConnParaConnectEvt(param_2);
      }
    }
    else if (cVar1 == '(') {
      fw_event_loop_remove_delayed(DAT_00478724);
      *DAT_004786ec = 0;
    }
    else if (cVar1 == ')') {
      _connUpdateFinishInd(param_2);
    }
    else if (cVar1 == '@') {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00478750,DAT_0047874c,DAT_00478748,0x23e,DAT_0047878c);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00478790,DAT_00478790);
      }
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00478750,DAT_0047874c,DAT_00478748,0x243,DAT_00478794,param_2[3],
                     param_2[4],param_2[5],param_2[6]);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x11000000,DAT_00478798,DAT_00478798,param_2[3],param_2[4],param_2[5],
                            param_2[6]);
      }
    }
    else if (cVar1 == -0x5d) {
      if (iVar6 == 0) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00478750,DAT_0047874c,DAT_00478748,0x20e,DAT_00478744,*param_2);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_00478754,DAT_00478754,*param_2);
        }
        *DAT_004786ec = 0;
      }
      else {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00478750,DAT_0047874c,DAT_00478748,0x212,DAT_00478758,param_2);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_0047875c,DAT_0047875c,param_2);
        }
        iVar5 = FUN_004b8128();
        piVar4 = DAT_00478720;
        if (iVar5 == 4) {
          *DAT_00478720 = DAT_00478760;
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(4,DAT_00478750,DAT_0047874c,DAT_00478748,0x215,DAT_00478764,
                         *(undefined2 *)(*piVar4 + 4),*(undefined2 *)(*piVar4 + 6));
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x10800000,DAT_00478768,DAT_00478768,*(undefined2 *)(*piVar4 + 4),
                                *(undefined2 *)(*piVar4 + 6));
          }
          _bleSlaveConnUpdate(0xa3,iVar6);
        }
        else {
          *DAT_00478720 = DAT_0047871c;
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(4,DAT_00478750,DAT_0047874c,DAT_00478748,0x219,DAT_0047876c,
                         *(undefined2 *)(*piVar4 + 4),*(undefined2 *)(*piVar4 + 6));
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x10800000,DAT_00478770,DAT_00478770,*(undefined2 *)(*piVar4 + 4),
                                *(undefined2 *)(*piVar4 + 6));
          }
          _bleSlaveConnUpdate(0xa3,iVar6);
        }
        *DAT_004786bc = 0xa3;
      }
    }
    else if (cVar1 == -0x5c) {
      if (iVar6 == 0) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00478750,DAT_0047874c,DAT_00478748,0x222,DAT_00478774,*param_2);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_00478778,DAT_00478778,*param_2);
        }
        *DAT_004786ec = 0;
      }
      else {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00478750,DAT_0047874c,DAT_00478748,0x226,DAT_0047877c,param_2);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_00478780,DAT_00478780,param_2);
        }
        piVar4 = DAT_00478720;
        *DAT_00478720 = DAT_004786c8;
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00478750,DAT_0047874c,DAT_00478748,0x228,DAT_00478784,
                       *(undefined2 *)(*piVar4 + 4),*(undefined2 *)(*piVar4 + 6));
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_00478788,DAT_00478788,*(undefined2 *)(*piVar4 + 4),
                              *(undefined2 *)(*piVar4 + 6));
        }
        _bleSlaveConnUpdate(0xa4,iVar6);
        *DAT_004786bc = 0xa4;
      }
    }
    else if (cVar1 == -0x47) {
      uVar2 = param_2[4];
      iVar6 = FUN_0043d0ce();
      uVar3 = (undefined1)uVar2;
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00478750,DAT_0047874c,DAT_00478748,0x249,DAT_0047879c,uVar3);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004787a0,DAT_004787a0,uVar3);
      }
      _connectParamReq_impl(uVar3);
    }
  }
  return;
}

