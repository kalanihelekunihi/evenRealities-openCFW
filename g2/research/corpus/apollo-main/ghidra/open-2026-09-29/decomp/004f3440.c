
undefined4 FUN_004f3440(char *param_1,int param_2)

{
  byte bVar1;
  int *piVar2;
  int *piVar3;
  uint *puVar4;
  uint *puVar5;
  undefined4 *puVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  int iVar10;
  uint local_80;
  undefined4 local_7c;
  uint local_78;
  uint local_74;
  undefined4 local_70;
  undefined4 local_60;
  undefined4 local_50;
  
  piVar2 = DAT_004f3f74;
  if (*DAT_004f3f74 == 0) {
    iVar7 = FUN_0043d0ce();
    if (iVar7 << 0x1e < 0) {
      local_7c = DAT_004f3f78;
      local_80 = 0x6c8;
      FUN_0043d574(2,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
    }
    iVar7 = FUN_0043d0ce();
    if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004f3f88);
    }
  }
  else if (param_2 == 0) {
    iVar7 = FUN_0043d0ce();
    if (iVar7 << 0x1e < 0) {
      local_7c = DAT_004f3f8c;
      local_80 = 0x6cd;
      FUN_0043d574(2,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
    }
    iVar7 = FUN_0043d0ce();
    if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004f3f90,DAT_004f3f90);
    }
  }
  else if (*param_1 == '\0') {
    bVar1 = param_1[1];
    uVar8 = *(uint *)(param_1 + 2);
    iVar7 = FUN_0043d0ce();
    if (iVar7 << 0x1e < 0) {
      local_78 = (uint)bVar1;
      local_7c = DAT_004f3f94;
      local_80 = 0x6d6;
      local_74 = uVar8;
      FUN_0043d574(3,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
    }
    iVar7 = FUN_0043d0ce();
    if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
      local_80 = uVar8;
      compress_log_output(0xc800000,DAT_004f3f98,DAT_004f3f98,bVar1);
    }
    piVar3 = DAT_004f3fc8;
    if (bVar1 == 10) {
      if ((*DAT_004f3fb0 == 1) || (*DAT_004f4608 == 1)) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          local_7c = DAT_004f460c;
          local_80 = 0x77a;
          FUN_0043d574(4,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004f4610,DAT_004f4610);
        }
      }
      else if ((*DAT_004f3fac == 0) && (*piVar2 == 1)) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          local_7c = DAT_004f4614;
          local_80 = 0x780;
          FUN_0043d574(3,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_004f4618,DAT_004f4618);
        }
        FUN_004f1544();
        ui_common_api_fn_00509f52(*DAT_004f3fc8);
        FUN_004fe1b4(3,*DAT_004f3fd4);
      }
      else if ((*DAT_004f3fac == 1) && (*piVar2 == 1)) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          local_7c = DAT_004f461c;
          local_80 = 0x78b;
          FUN_0043d574(3,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_004f4620,DAT_004f4620);
        }
      }
    }
    else if (bVar1 == 0x44) {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        local_7c = DAT_004f3f9c;
        local_80 = 0x6da;
        FUN_0043d574(3,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004f3fa0,DAT_004f3fa0);
      }
      puVar4 = DAT_004f3fb4;
      piVar3 = DAT_004f3fb0;
      if (*piVar2 == 1) {
        if ((*DAT_004f3fac == 0) || ((*DAT_004f3fb0 == 1 && (*DAT_004f3f70 == 1)))) {
          if (*DAT_004f3fb4 == 0) {
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              local_7c = DAT_004f3fb8;
              local_80 = 0x6e5;
              FUN_0043d574(2,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0x8000000,DAT_004f3fbc,DAT_004f3fbc);
            }
          }
          else if (*DAT_004f3fb0 == 1) {
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              local_7c = DAT_004f3fc0;
              local_80 = 0x6eb;
              FUN_0043d574(4,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0x10000000,DAT_004f3fc4,DAT_004f3fc4);
            }
            ui_common_api_fn_00509ca2(*DAT_004f3fc8,param_1,6);
          }
          else {
            uVar8 = FUN_0044e498(*DAT_004f3fb4);
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              local_7c = DAT_004f3fcc;
              local_80 = 0x6f2;
              local_78 = uVar8;
              FUN_0043d574(3,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0xc400000,DAT_004f3fd0,DAT_004f3fd0,uVar8);
            }
            piVar2 = DAT_004f3fe4;
            puVar5 = DAT_004f3fd4;
            if ((int)*DAT_004f3fd4 < *DAT_004f3fd8 + -1) {
              iVar7 = FUN_0043d0ce();
              if (iVar7 << 0x1e < 0) {
                local_78 = *puVar5;
                local_7c = DAT_004f3fdc;
                local_80 = 0x6f6;
                FUN_0043d574(4,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
              }
              iVar7 = FUN_0043d0ce();
              if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
                compress_log_output(0x10400000,DAT_004f3fe0,DAT_004f3fe0,*puVar5);
              }
              FUN_004f28f0(*puVar5 + 1,200);
              FUN_004fe1b4(2,*puVar5);
            }
            else if (*DAT_004f3fe4 == 0) {
              iVar7 = FUN_0043d0ce();
              if (iVar7 << 0x1e < 0) {
                local_7c = DAT_004f4010;
                local_80 = 0x72b;
                FUN_0043d574(4,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
              }
              iVar7 = FUN_0043d0ce();
              if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
                compress_log_output(0x10000000,DAT_004f4014,DAT_004f4014);
              }
            }
            else {
              iVar7 = FUN_0043d0ce();
              if (iVar7 << 0x1e < 0) {
                local_7c = DAT_004f3fe8;
                local_80 = 0x6fd;
                FUN_0043d574(3,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
              }
              iVar7 = FUN_0043d0ce();
              if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
                compress_log_output(0xc000000,DAT_004f3fec,DAT_004f3fec);
              }
              uVar9 = FUN_0043fce0(*piVar2);
              if ((int)(uVar8 + 0xee) < (int)uVar9) {
                iVar7 = FUN_0043d0ce();
                if (iVar7 << 0x1e < 0) {
                  local_7c = DAT_004f3ff0;
                  local_80 = 0x704;
                  local_78 = uVar9;
                  local_74 = uVar8;
                  FUN_0043d574(4,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
                }
                iVar7 = FUN_0043d0ce();
                if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
                  local_80 = uVar8;
                  compress_log_output(0x10800000,DAT_004f3ff4,DAT_004f3ff4,uVar9);
                }
                FUN_004f0e94(*puVar5);
                iVar7 = FUN_0043fdda(*piVar2);
                *piVar3 = 1;
                FUN_004503d6(&local_80);
                local_80 = *puVar4;
                local_7c = DAT_004f3ff8;
                FUN_004506ce(&local_80,uVar8,uVar9 - (0x120 - iVar7) / 2);
                local_50 = 200;
                local_60 = DAT_004f3ffc;
                local_70 = DAT_004f4000;
                FUN_00450408(&local_80);
              }
              else {
                iVar7 = FUN_0043d0ce();
                if (iVar7 << 0x1e < 0) {
                  local_7c = DAT_004f4004;
                  local_80 = 0x725;
                  FUN_0043d574(3,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
                }
                iVar7 = FUN_0043d0ce();
                if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
                  compress_log_output(0xc000000,DAT_004f4008,DAT_004f4008);
                }
                FUN_004f0e94(*puVar5);
                FUN_004f2bbc(*piVar2,DAT_004f400c);
                FUN_004fe0aa();
              }
            }
          }
        }
        else if (*DAT_004f3fac == 1) {
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            local_7c = DAT_004f4018;
            local_80 = 0x730;
            FUN_0043d574(4,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_004f401c,DAT_004f401c);
          }
          FUN_004f2554(1,uVar8 >> 0x10,uVar8 & 0xffff);
        }
      }
      else {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          local_7c = DAT_004f3fa4;
          local_80 = 0x6dd;
          FUN_0043d574(2,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_004f3fa8,DAT_004f3fa8);
        }
      }
    }
    else if (bVar1 == 0x45) {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        local_7c = DAT_004f4020;
        local_80 = 0x737;
        FUN_0043d574(3,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004f4024,DAT_004f4024);
      }
      if (*piVar2 == 1) {
        if ((*DAT_004f3fac == 0) || ((*DAT_004f3fb0 == 1 && (*DAT_004f3f70 == 1)))) {
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            local_7c = DAT_004f4028;
            local_80 = 0x740;
            FUN_0043d574(3,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            compress_log_output(0xc000000,DAT_004f402c,DAT_004f402c);
          }
          puVar4 = DAT_004f3fb4;
          if (*DAT_004f3fb4 == 0) {
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              local_7c = DAT_004f3fb8;
              local_80 = 0x743;
              FUN_0043d574(2,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0x8000000,DAT_004f3fbc,DAT_004f3fbc);
            }
          }
          else if (*DAT_004f3fb0 == 1) {
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              local_7c = DAT_004f45d8;
              local_80 = 0x749;
              FUN_0043d574(4,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0x10000000,DAT_004f45dc,DAT_004f45dc);
            }
            ui_common_api_fn_00509ca2(*DAT_004f3fc8,param_1,6);
          }
          else {
            uVar8 = FUN_0044e498(*DAT_004f3fb4);
            piVar2 = DAT_004f3fd8;
            if (((*DAT_004f3fe4 == 0) || (*DAT_004f3fd8 < 1)) ||
               (uVar9 = FUN_004f2804(*DAT_004f3fd8 + -1), (int)uVar8 <= (int)(uVar9 + 10))) {
              puVar5 = DAT_004f3fd4;
              if ((int)*DAT_004f3fd4 < 1) {
                if ((int)uVar8 < 0x15) {
                  iVar7 = FUN_0043d0ce();
                  if (iVar7 << 0x1e < 0) {
                    local_7c = DAT_004f45f8;
                    local_80 = 0x76a;
                    local_78 = uVar8;
                    FUN_0043d574(4,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
                  }
                  iVar7 = FUN_0043d0ce();
                  if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
                    compress_log_output(0x10400000,DAT_004f45fc,DAT_004f45fc,uVar8);
                  }
                  FUN_004f11c0();
                }
                else {
                  iVar7 = FUN_0043d0ce();
                  if (iVar7 << 0x1e < 0) {
                    local_7c = DAT_004f45f0;
                    local_80 = 0x765;
                    local_78 = uVar8;
                    FUN_0043d574(4,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
                  }
                  iVar7 = FUN_0043d0ce();
                  if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
                    compress_log_output(0x10400000,DAT_004f45f4,DAT_004f45f4,uVar8);
                  }
                  FUN_0044ea04(*puVar4,0,1);
                }
              }
              else {
                iVar7 = FUN_0043d0ce();
                if (iVar7 << 0x1e < 0) {
                  local_78 = *puVar5;
                  local_7c = DAT_004f45e8;
                  local_80 = 0x75e;
                  FUN_0043d574(4,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
                }
                iVar7 = FUN_0043d0ce();
                if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
                  compress_log_output(0x10400000,DAT_004f45ec,DAT_004f45ec,*puVar5);
                }
                FUN_004f28f0(*puVar5 - 1,200);
                FUN_004fe1b4(2,*puVar5);
              }
            }
            else {
              iVar7 = FUN_0043d0ce();
              if (iVar7 << 0x1e < 0) {
                local_7c = DAT_004f45e0;
                local_80 = 0x756;
                local_78 = uVar8;
                local_74 = uVar9;
                FUN_0043d574(4,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
              }
              iVar7 = FUN_0043d0ce();
              if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
                local_80 = uVar9;
                compress_log_output(0x10800000,DAT_004f45e4,DAT_004f45e4,uVar8);
              }
              FUN_004f28f0(*piVar2 + -1,200);
            }
          }
        }
        else if (*DAT_004f3fac == 1) {
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            local_7c = DAT_004f4600;
            local_80 = 0x770;
            FUN_0043d574(4,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_004f4604,DAT_004f4604);
          }
          FUN_004f2554(0xffffffff,uVar8 >> 0x10,uVar8 & 0xffff);
        }
      }
      else {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          local_7c = DAT_004f3fa4;
          local_80 = 0x73a;
          FUN_0043d574(2,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_004f3fa8,DAT_004f3fa8);
        }
      }
    }
    else if (bVar1 == 0x48) {
      if (*piVar2 == 1) {
        if (*DAT_004f3fac == 0) {
          if (*DAT_004f3fc8 != 0) {
            ui_common_api_fn_00509c96(*DAT_004f3fc8);
            *piVar3 = 0;
          }
          puVar6 = DAT_004f4624;
          iVar7 = FUN_0044ddea(*DAT_004f4624);
          while (iVar7 = iVar7 + -1, -1 < iVar7) {
            iVar10 = FUN_0044dce2(*puVar6,iVar7);
            if (iVar10 != 0) {
              FUN_0044d7b8();
            }
          }
          *piVar2 = 0;
          piVar2 = DAT_004f4628;
          if (*(int *)(DAT_004f462c + *DAT_004f4628 * 8 + 4) != 0) {
            FUN_0044d878(*(undefined4 *)(DAT_004f462c + *DAT_004f4628 * 8 + 4));
          }
          FUN_004efffc();
          FUN_004e92f4();
          FUN_005000cc(*piVar2,1);
          FUN_004fe1b4(1,0);
        }
        else if (*DAT_004f3fac == 1) {
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            local_7c = DAT_004f4630;
            local_80 = 0x7b4;
            FUN_0043d574(3,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            compress_log_output(0xc000000,DAT_004f4634,DAT_004f4634);
          }
          ui_common_api_fn_00509f52(*DAT_004f3fc8);
          FUN_004f18ac();
          FUN_004fe1b4(4,*DAT_004f3fd4);
        }
      }
      else {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          local_7c = DAT_004f3fa4;
          local_80 = 0x794;
          FUN_0043d574(2,DAT_004f3f84,DAT_004f3f80,DAT_004f3f7c);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_004f3fa8,DAT_004f3fa8);
        }
      }
    }
  }
  return 0;
}

