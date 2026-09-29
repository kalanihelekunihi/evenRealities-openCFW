
undefined4 TPL_ReceivePacket(char param_1,char *param_2,ushort param_3)

{
  short sVar1;
  uint *puVar2;
  short sVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  
  uVar4 = DAT_004b9a18;
  if (param_2 == (char *)0x0) {
    tpl_reset_receive_contexts_004b9984();
    uVar4 = 6;
  }
  else if (param_3 < 8) {
    tpl_reset_receive_contexts_004b9984();
    uVar4 = 0xb;
  }
  else if (*param_2 == -0x56) {
    if ((param_2[3] == '\0') && (param_3 == 8)) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(3,DAT_004b9a10,DAT_004b9a0c,DAT_004b9a08,400,DAT_004b9a04,
                     ((byte)param_2[7] & 0x1f) >> 1);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_004b9a14,DAT_004b9a14,((byte)param_2[7] & 0x1f) >> 1);
      }
      tpl_reset_receive_contexts_004b9984();
      uVar4 = 0;
    }
    else {
      fw_event_loop_remove_delayed(DAT_004b9a18);
      puVar2 = DAT_004b9a1c;
      if (param_2[4] == '\x01') {
        *DAT_004b9a1c = (byte)param_2[3] - 2;
        sVar1 = *(short *)(param_2 + *puVar2 + 8);
        sVar3 = FUN_0049acd4(param_2 + 8,*puVar2,0);
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004b9a10,DAT_004b9a0c,DAT_004b9a08,0x1a7,DAT_004b9a20,*puVar2);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_004b9a24,DAT_004b9a24,*puVar2);
        }
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004b9a10,DAT_004b9a0c,DAT_004b9a08,0x1a8,DAT_004b9a28,sVar1,sVar3);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_004b9a2c,DAT_004b9a2c,sVar1,sVar3);
        }
        if (sVar3 == sVar1) {
          if (param_1 == '\0') {
            if ((((byte)param_2[7] & 0x3f) >> 5 == 0) || (*(int *)(DAT_004b9a30 + 4) == 0)) {
              if ((((byte)param_2[7] & 0x3f) >> 5 == 0) && (*(int *)(DAT_004b9a30 + 8) != 0)) {
                (**(code **)(DAT_004b9a30 + 8))(param_2[6],param_2 + 8,*puVar2 & 0xffff);
              }
            }
            else {
              (**(code **)(DAT_004b9a30 + 4))(param_2[6],param_2 + 8,*puVar2 & 0xffff,DAT_004b9a34);
            }
          }
          else {
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              FUN_0043d574(1,DAT_004b9a10,DAT_004b9a0c,DAT_004b9a08,0x1b5,DAT_004b9a38,param_1);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0x4400000,DAT_004b9a3c,DAT_004b9a3c,param_1);
            }
          }
        }
        else {
          _tplReponse(param_1,param_2[2],param_2[6],1);
        }
        uVar4 = 0;
      }
      else {
        iVar5 = _getOrCreateContext(param_2,param_1);
        if (iVar5 == 0) {
          if ((byte)param_2[5] < (byte)param_2[4]) {
            tpl_schedule_rx_timeout_004b8c44(param_1,param_2[6],param_2[2]);
            uVar4 = 0;
          }
          else {
            _tplReponse(param_1,param_2[2],param_2[6],1);
            uVar4 = 1;
          }
        }
        else if (param_2[4] == *(char *)(iVar5 + 0x32)) {
          iVar6 = tpl_context_packet_seen_004b8c14(iVar5,param_2[5] + -1);
          if (iVar6 == 0) {
            FUN_00439be4(*(int *)(iVar5 + 8) + (uint)*(ushort *)(iVar5 + 2),param_2 + 8,param_2[3]);
            tpl_context_mark_packet_004b8bdc(iVar5,param_2[5] + -1);
            *(ushort *)(iVar5 + 2) = *(short *)(iVar5 + 2) + (ushort)(byte)param_2[3];
            if ((byte)param_2[5] < (byte)param_2[4]) {
              tpl_schedule_rx_timeout_004b8c44(param_1,param_2[6],param_2[2]);
              uVar4 = 0;
            }
            else {
              *(short *)(iVar5 + 2) = *(short *)(iVar5 + 2) + -2;
              sVar1 = *(short *)(*(int *)(iVar5 + 8) + (uint)*(ushort *)(iVar5 + 2));
              sVar3 = FUN_0049acd4(*(undefined4 *)(iVar5 + 8),*(undefined2 *)(iVar5 + 2),0);
              iVar6 = FUN_0043d0ce();
              if (iVar6 << 0x1e < 0) {
                FUN_0043d574(4,DAT_004b9a10,DAT_004b9a0c,DAT_004b9a08,0x1ee,DAT_004b9a20,
                             *(undefined2 *)(iVar5 + 2));
              }
              iVar6 = FUN_0043d0ce();
              if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                compress_log_output(0x10400000,DAT_004b9a24,DAT_004b9a24,*(undefined2 *)(iVar5 + 2))
                ;
              }
              iVar6 = FUN_0043d0ce();
              if (iVar6 << 0x1e < 0) {
                FUN_0043d574(4,DAT_004b9a10,DAT_004b9a0c,DAT_004b9a08,0x1ef,DAT_004b9a28,sVar1,sVar3
                            );
              }
              iVar6 = FUN_0043d0ce();
              if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                compress_log_output(0x10800000,DAT_004b9a2c,DAT_004b9a2c,sVar1,sVar3);
              }
              fw_event_loop_remove_delayed(uVar4);
              if (sVar3 == sVar1) {
                if (param_1 == '\0') {
                  if ((((byte)param_2[7] & 0x3f) >> 5 == 0) || (*(int *)(DAT_004b9a30 + 4) == 0)) {
                    if ((((byte)param_2[7] & 0x3f) >> 5 == 0) && (*(int *)(DAT_004b9a30 + 8) != 0))
                    {
                      (**(code **)(DAT_004b9a30 + 8))
                                (param_2[6],*(undefined4 *)(iVar5 + 8),*(undefined2 *)(iVar5 + 2));
                    }
                  }
                  else {
                    (**(code **)(DAT_004b9a30 + 4))
                              (param_2[6],*(undefined4 *)(iVar5 + 8),*(undefined2 *)(iVar5 + 2),
                               DAT_004b9a34);
                  }
                }
                else {
                  iVar6 = FUN_0043d0ce();
                  if (iVar6 << 0x1e < 0) {
                    FUN_0043d574(1,DAT_004b9a10,DAT_004b9a0c,DAT_004b9a08,0x1ff,DAT_004b9a38,param_1
                                );
                  }
                  iVar6 = FUN_0043d0ce();
                  if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                    compress_log_output(0x4400000,DAT_004b9a3c,DAT_004b9a3c,param_1);
                  }
                }
                tpl_context_free_004b8ba2(iVar5);
                uVar4 = 0;
              }
              else {
                tpl_context_free_004b8ba2(iVar5);
                _tplReponse(param_1,param_2[2],param_2[6],1);
                uVar4 = 1;
              }
            }
          }
          else {
            if ((byte)param_2[5] < (byte)param_2[4]) {
              tpl_schedule_rx_timeout_004b8c44(param_1,param_2[6],param_2[2]);
            }
            else {
              tpl_context_free_004b8ba2(iVar5);
            }
            uVar4 = 0xd;
          }
        }
        else {
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(1,DAT_004b9a10,DAT_004b9a0c,DAT_004b9a08,0x1cb,DAT_004b9a40,param_2[4],
                         *(undefined1 *)(iVar5 + 0x32),param_2[5]);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x4c00000,DAT_004b9a44,DAT_004b9a44,param_2[4],
                                *(undefined1 *)(iVar5 + 0x32),param_2[5]);
          }
          tpl_context_free_004b8ba2(iVar5);
          _tplReponse(param_1,param_2[2],param_2[6],1);
          uVar4 = 1;
        }
      }
    }
  }
  else {
    tpl_reset_receive_contexts_004b9984();
    uVar4 = 10;
  }
  return uVar4;
}

