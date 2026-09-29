
undefined4 FUN_004de354(int *param_1,byte param_2)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  uint local_30;
  int local_2c;
  int local_28;
  uint local_24;
  
  if (param_1 == (int *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x310,DAT_004dedd0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004dede0);
    }
    uVar2 = 0xffffffff;
  }
  else if ((*param_1 == 0) || (param_1[1] == 0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x315,DAT_004dede4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004dede8,DAT_004dede8);
    }
    uVar2 = 0xffffffff;
  }
  else if (((param_2 == 2) || (param_2 == 0)) || (param_2 == 1)) {
    if ((char)param_1[0x15f] == '\0') {
      iVar1 = param_1[0x16];
      if (iVar1 < 1) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x32c,DAT_004dee04);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_004dee08,DAT_004dee08);
        }
        uVar2 = 0xffffffff;
      }
      else {
        uVar4 = param_1[0x1a];
        if ((int)uVar4 < iVar1) {
          iVar5 = param_1[0x17] - param_1[0x18];
          if (param_2 == 0) {
            if (param_1[0x17] < iVar1 + -1) {
              iVar3 = FUN_0043d0ce();
              if (iVar3 << 0x1e < 0) {
                local_28 = param_1[0x18];
                local_30 = param_1[0x17];
                local_2c = iVar5;
                local_24 = uVar4;
                FUN_0043d574(4,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x3a9,DAT_004dee54);
              }
              iVar3 = FUN_0043d0ce();
              if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
                local_30 = uVar4;
                compress_log_output(0x11000000,DAT_004dee58,DAT_004dee58,param_1[0x17],iVar5,
                                    param_1[0x18]);
              }
              if (iVar5 < (int)(uVar4 - 2)) {
                FUN_004dcd92(param_1);
                param_1[0x17] = param_1[0x17] + 1;
                iVar1 = FUN_0043d0ce();
                if (iVar1 << 0x1e < 0) {
                  local_30 = param_1[0x17];
                  FUN_0043d574(4,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x3af,DAT_004dee3c);
                }
                iVar1 = FUN_0043d0ce();
                if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                  compress_log_output(0x10400000,DAT_004dee40,DAT_004dee40,param_1[0x17]);
                }
                FUN_004dcdbe(param_1);
                *(undefined1 *)(param_1 + 0x15f) = 1;
                FUN_004dd414(param_1);
              }
              else if (iVar5 == uVar4 - 2) {
                iVar1 = iVar1 - uVar4;
                if (iVar1 < 0) {
                  iVar1 = 0;
                }
                if (param_1[0x18] < iVar1) {
                  FUN_004dcd92(param_1);
                  param_1[0x18] = param_1[0x18] + 1;
                  param_1[0x17] = param_1[0x17] + 1;
                  iVar1 = FUN_004dceb0(param_1,param_1[0x17]);
                  iVar5 = FUN_0043d0ce();
                  if (iVar5 << 0x1e < 0) {
                    local_2c = param_1[0x18];
                    local_30 = param_1[0x17];
                    local_28 = iVar1;
                    FUN_0043d574(4,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x3bf,DAT_004dee44);
                  }
                  iVar5 = FUN_0043d0ce();
                  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                    compress_log_output(0x10c00000,DAT_004dee48,DAT_004dee48,param_1[0x17],
                                        param_1[0x18],iVar1);
                  }
                  *(undefined1 *)(param_1 + 0x15f) = 1;
                  FUN_004dcfe6(param_1,iVar1,200);
                }
                else {
                  FUN_004dcd92(param_1);
                  param_1[0x17] = param_1[0x17] + 1;
                  iVar1 = FUN_0043d0ce();
                  if (iVar1 << 0x1e < 0) {
                    local_30 = param_1[0x17];
                    FUN_0043d574(4,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x3c6,DAT_004dee5c);
                  }
                  iVar1 = FUN_0043d0ce();
                  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                    compress_log_output(0x10400000,DAT_004dee60,DAT_004dee60,param_1[0x17]);
                  }
                  FUN_004dcdbe(param_1);
                  *(undefined1 *)(param_1 + 0x15f) = 1;
                  FUN_004dd414(param_1);
                }
              }
              else {
                FUN_004dcd92(param_1);
                param_1[0x17] = param_1[0x17] + 1;
                iVar1 = FUN_0043d0ce();
                if (iVar1 << 0x1e < 0) {
                  local_30 = param_1[0x17];
                  FUN_0043d574(4,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x3cf,DAT_004dee3c);
                }
                iVar1 = FUN_0043d0ce();
                if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                  compress_log_output(0x10400000,DAT_004dee40,DAT_004dee40,param_1[0x17]);
                }
                FUN_004dcdbe(param_1);
                *(undefined1 *)(param_1 + 0x15f) = 1;
                FUN_004dd414(param_1);
              }
            }
            else {
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                FUN_0043d574(4,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x3d6,DAT_004dee24);
              }
              iVar1 = FUN_0043d0ce();
              if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                compress_log_output(0x10000000,DAT_004dee28,DAT_004dee28);
              }
              *(undefined1 *)(param_1 + 0x15f) = 1;
              FUN_004dd1c4(param_1,0);
            }
          }
          else if (param_2 == 2) {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              local_2c = (int)param_1 + param_1[0x17] * 0x40 + 0x6e;
              local_30 = param_1[0x17];
              FUN_0043d574(3,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x3de,DAT_004dee2c);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0xc800000,DAT_004dee30,DAT_004dee30,param_1[0x17],
                                  (int)param_1 + param_1[0x17] * 0x40 + 0x6e);
            }
            if (param_1[0x15d] != 0) {
              (*(code *)param_1[0x15d])
                        (param_1[0x17],(int)param_1 + param_1[0x17] * 0x40 + 0x6e,param_1[0x15e]);
            }
          }
          else if (param_2 < 2) {
            if (param_1[0x17] < 1) {
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                FUN_0043d574(4,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x39f,DAT_004dee14);
              }
              iVar1 = FUN_0043d0ce();
              if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                compress_log_output(0x10000000,DAT_004dee18,DAT_004dee18);
              }
              *(undefined1 *)(param_1 + 0x15f) = 1;
              FUN_004dd1c4(param_1,1);
            }
            else {
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                local_28 = param_1[0x18];
                local_30 = param_1[0x17];
                local_2c = iVar5;
                local_24 = uVar4;
                FUN_0043d574(4,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x375,DAT_004dee34);
              }
              iVar1 = FUN_0043d0ce();
              if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                local_30 = uVar4;
                compress_log_output(0x11000000,DAT_004dee38,DAT_004dee38,param_1[0x17],iVar5,
                                    param_1[0x18]);
              }
              if (iVar5 < 2) {
                if (iVar5 == 1) {
                  if (param_1[0x18] < 1) {
                    FUN_004dcd92(param_1);
                    param_1[0x17] = param_1[0x17] + -1;
                    iVar1 = FUN_0043d0ce();
                    if (iVar1 << 0x1e < 0) {
                      local_30 = param_1[0x17];
                      FUN_0043d574(4,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x38f,DAT_004dee4c);
                    }
                    iVar1 = FUN_0043d0ce();
                    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                      compress_log_output(0x10400000,DAT_004dee50,DAT_004dee50,param_1[0x17]);
                    }
                    FUN_004dcdbe(param_1);
                    *(undefined1 *)(param_1 + 0x15f) = 1;
                    FUN_004dd414(param_1);
                  }
                  else {
                    FUN_004dcd92(param_1);
                    param_1[0x18] = param_1[0x18] + -1;
                    param_1[0x17] = param_1[0x17] + -1;
                    iVar1 = FUN_004dceb0(param_1,param_1[0x17]);
                    iVar5 = FUN_0043d0ce();
                    if (iVar5 << 0x1e < 0) {
                      local_2c = param_1[0x18];
                      local_30 = param_1[0x17];
                      local_28 = iVar1;
                      FUN_0043d574(4,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x388,DAT_004dee44);
                    }
                    iVar5 = FUN_0043d0ce();
                    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                      compress_log_output(0x10c00000,DAT_004dee48,DAT_004dee48,param_1[0x17],
                                          param_1[0x18],iVar1);
                    }
                    *(undefined1 *)(param_1 + 0x15f) = 1;
                    FUN_004dcfe6(param_1,iVar1,200);
                  }
                }
                else {
                  FUN_004dcd92(param_1);
                  param_1[0x17] = param_1[0x17] + -1;
                  iVar1 = FUN_0043d0ce();
                  if (iVar1 << 0x1e < 0) {
                    local_30 = param_1[0x17];
                    FUN_0043d574(4,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x398,DAT_004dee3c);
                  }
                  iVar1 = FUN_0043d0ce();
                  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                    compress_log_output(0x10400000,DAT_004dee40,DAT_004dee40,param_1[0x17]);
                  }
                  FUN_004dcdbe(param_1);
                  *(undefined1 *)(param_1 + 0x15f) = 1;
                  FUN_004dd414(param_1);
                }
              }
              else {
                FUN_004dcd92(param_1);
                param_1[0x17] = param_1[0x17] + -1;
                iVar1 = FUN_0043d0ce();
                if (iVar1 << 0x1e < 0) {
                  local_30 = param_1[0x17];
                  FUN_0043d574(4,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x37b,DAT_004dee3c);
                }
                iVar1 = FUN_0043d0ce();
                if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                  compress_log_output(0x10400000,DAT_004dee40,DAT_004dee40,param_1[0x17]);
                }
                FUN_004dcdbe(param_1);
                *(undefined1 *)(param_1 + 0x15f) = 1;
                FUN_004dd414(param_1);
              }
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              local_30 = (uint)param_2;
              FUN_0043d574(2,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x3ea,DAT_004dedec);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0x8400000,DAT_004dedf0,DAT_004dedf0,param_2);
            }
          }
          uVar2 = 0;
        }
        else {
          if (param_2 == 0) {
            if (param_1[0x17] < iVar1 + -1) {
              FUN_004dcd92(param_1);
              param_1[0x17] = param_1[0x17] + 1;
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                local_30 = param_1[0x17];
                FUN_0043d574(4,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x348,DAT_004dee1c);
              }
              iVar1 = FUN_0043d0ce();
              if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                compress_log_output(0x10400000,DAT_004dee20,DAT_004dee20,param_1[0x17]);
              }
              FUN_004dcdbe(param_1);
              *(undefined1 *)(param_1 + 0x15f) = 1;
              FUN_004dd414(param_1);
            }
            else {
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                FUN_0043d574(4,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x34d,DAT_004dee24);
              }
              iVar1 = FUN_0043d0ce();
              if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                compress_log_output(0x10000000,DAT_004dee28,DAT_004dee28);
              }
              *(undefined1 *)(param_1 + 0x15f) = 1;
              FUN_004dd1c4(param_1,0);
            }
          }
          else if (param_2 == 2) {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              local_2c = (int)param_1 + param_1[0x17] * 0x40 + 0x6e;
              local_30 = param_1[0x17];
              FUN_0043d574(3,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x355,DAT_004dee2c);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0xc800000,DAT_004dee30,DAT_004dee30,param_1[0x17],
                                  (int)param_1 + param_1[0x17] * 0x40 + 0x6e);
            }
            if (param_1[0x15d] != 0) {
              (*(code *)param_1[0x15d])
                        (param_1[0x17],(int)param_1 + param_1[0x17] * 0x40 + 0x6e,param_1[0x15e]);
            }
          }
          else if (param_2 < 2) {
            if (param_1[0x17] < 1) {
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                FUN_0043d574(4,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x33e,DAT_004dee14);
              }
              iVar1 = FUN_0043d0ce();
              if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                compress_log_output(0x10000000,DAT_004dee18,DAT_004dee18);
              }
              *(undefined1 *)(param_1 + 0x15f) = 1;
              FUN_004dd1c4(param_1,1);
            }
            else {
              FUN_004dcd92(param_1);
              param_1[0x17] = param_1[0x17] + -1;
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                local_30 = param_1[0x17];
                FUN_0043d574(4,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x339,DAT_004dee0c);
              }
              iVar1 = FUN_0043d0ce();
              if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                compress_log_output(0x10400000,DAT_004dee10,DAT_004dee10,param_1[0x17]);
              }
              FUN_004dcdbe(param_1);
              *(undefined1 *)(param_1 + 0x15f) = 1;
              FUN_004dd414(param_1);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              local_30 = (uint)param_2;
              FUN_0043d574(2,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x361,DAT_004dedec);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0x8400000,DAT_004dedf0,DAT_004dedf0,param_2);
            }
          }
          uVar2 = 0;
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_30 = (uint)param_2;
        FUN_0043d574(4,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x321,DAT_004dedf4);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004dedf8,DAT_004dedf8,param_2);
      }
      local_30 = CONCAT31(local_30._1_3_,param_2);
      iVar1 = ui_common_api_fn_00509ca2(param_1[0x15c],&local_30,1);
      if (iVar1 == 0) {
        uVar2 = 0;
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x324,DAT_004dedfc);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_004dee00,DAT_004dee00);
        }
        uVar2 = 0xffffffff;
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_30 = (uint)param_2;
      FUN_0043d574(2,DAT_004deddc,DAT_004dedd8,DAT_004dedd4,0x31b,DAT_004dedec);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_004dedf0,DAT_004dedf0,param_2);
    }
    uVar2 = 1;
  }
  return uVar2;
}

