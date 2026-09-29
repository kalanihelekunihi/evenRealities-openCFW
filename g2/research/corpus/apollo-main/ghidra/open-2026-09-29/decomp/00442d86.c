
undefined4 FUN_00442d86(ushort *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  ushort uVar2;
  ushort uVar3;
  undefined4 *puVar4;
  char cVar5;
  int *piVar6;
  int iVar7;
  undefined4 uVar8;
  int local_40;
  int local_3c;
  uint local_38;
  int local_34;
  uint local_30;
  uint local_2c;
  int local_28;
  int local_24;
  int local_20;
  int local_1c;
  undefined4 uStack_18;
  
  puVar4 = DAT_00443750;
  local_2c = (uint)*param_1;
  uVar1 = *(uint *)(param_1 + 1);
  local_30 = *(uint *)(param_1 + 3);
  uStack_18 = param_4;
  piVar6 = (int *)FUN_0045f8e6(*DAT_00443750);
  if (piVar6 == (int *)0x0) {
    iVar7 = FUN_0043d0ce();
    if (iVar7 << 0x1e < 0) {
      local_3c = DAT_00443754;
      local_40 = 0x177;
      FUN_0043d574(2,DAT_00443760,DAT_0044375c,DAT_00443758);
    }
    iVar7 = FUN_0043d0ce();
    if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00443764,DAT_00443764);
    }
    uVar8 = 0xffffffff;
  }
  else {
    if (uVar1 == 0) {
      FUN_0045f8fc(*puVar4,10,&local_2c);
    }
    else if (uVar1 == 2) {
      FUN_0045f8fc(*puVar4,0x3f,&local_30);
    }
    else if (uVar1 < 2) {
      FUN_0045f8fc(*puVar4,0x48,&local_2c);
    }
    else if (uVar1 == 4) {
      uVar2 = param_1[3];
      uVar3 = param_1[4];
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        local_34 = (int)(short)uVar3;
        local_38 = (uint)(short)uVar2;
        local_3c = DAT_00443788;
        local_40 = 0x1ba;
        FUN_0043d574(4,DAT_00443760,DAT_0044375c,DAT_00443758);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        local_40 = (int)(short)uVar3;
        compress_log_output(0x10800000,DAT_0044378c,DAT_0044378c,(int)(short)uVar2);
      }
      local_40 = (int)(short)uVar2;
      local_3c = (int)(short)uVar3;
      FUN_0045f8fc(*puVar4,0x44,&local_40);
    }
    else if (uVar1 < 4) {
      iVar7 = FUN_00442d64();
      if (iVar7 == 0) {
        iVar7 = FUN_0045bbf4();
        if (iVar7 == 0) {
          if (*(char *)((int)piVar6 + 0xb) == '\0') {
            if (*piVar6 == 0xe0) {
              system_close_page_factory_0046ae9c(1,0xe0);
            }
            else {
              iVar7 = FUN_0045a568();
              if (iVar7 == 1) {
                FUN_00464b2e(3,0,0,0);
              }
            }
          }
          else if (*(char *)((int)piVar6 + 0xb) == '\x01') {
            if (*piVar6 == 3) {
              if (*piVar6 == 3) {
                FUN_00460374();
                FUN_0045faa8(*puVar4,0,3);
                if (*DAT_0044376c == 2) {
                  return 1;
                }
                *DAT_00443768 = 0;
              }
            }
            else {
              uVar8 = FUN_0045f840(*puVar4,3);
              iVar7 = FUN_0045f706(*puVar4,uVar8);
              if (iVar7 == 1) {
                FUN_0044228a(*piVar6,5,0,0);
              }
              cVar5 = FUN_0045faa8(*puVar4,2,3);
              if (cVar5 == '\x01') {
                uVar8 = FUN_0045f840(*puVar4,3);
                iVar7 = FUN_0045f706(*puVar4,uVar8);
                if (iVar7 == 1) {
                  *DAT_00443768 = 3;
                }
              }
            }
          }
        }
        else {
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            local_3c = DAT_00443770;
            local_40 = 0x19d;
            FUN_0043d574(4,DAT_00443760,DAT_0044375c,DAT_00443758);
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_00443774);
          }
          if (*piVar6 == 0x30) {
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              local_3c = DAT_00443778;
              local_40 = 0x19f;
              FUN_0043d574(3,DAT_00443760,DAT_0044375c,DAT_00443758);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0xc000000,DAT_0044377c,DAT_0044377c);
            }
            FUN_0045f8fc(*puVar4,8,&local_30);
          }
        }
      }
      else {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          local_3c = DAT_00443780;
          local_40 = 0x1a4;
          FUN_0043d574(4,DAT_00443760,DAT_0044375c,DAT_00443758);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_00443784,DAT_00443784);
        }
        FUN_0045f8fc(*puVar4,8,&local_30);
      }
    }
    else if (uVar1 == 6) {
      iVar7 = FUN_00442d64();
      if (iVar7 == 1) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          local_3c = DAT_00443790;
          local_40 = 0x1db;
          FUN_0043d574(4,DAT_00443760,DAT_0044375c,DAT_00443758);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_00443794,DAT_00443794);
        }
        FUN_0045f8fc(*puVar4,0x4b,&local_30);
      }
    }
    else if (uVar1 < 6) {
      uVar2 = param_1[3];
      uVar3 = param_1[4];
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        local_34 = (int)(short)uVar3;
        local_38 = (uint)(short)uVar2;
        local_3c = DAT_00443788;
        local_40 = 0x1c5;
        FUN_0043d574(4,DAT_00443760,DAT_0044375c,DAT_00443758);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        local_40 = (int)(short)uVar3;
        compress_log_output(0x10800000,DAT_0044378c,DAT_0044378c,(int)(short)uVar2);
      }
      local_20 = (int)(short)uVar2;
      local_1c = (int)(short)uVar3;
      FUN_0045f8fc(*puVar4,0x45,&local_20);
    }
    else if (uVar1 == 8) {
      FUN_0045f8fc(*puVar4,0x40,&local_30);
    }
    else if (uVar1 < 8) {
      FUN_0045f8fc(*puVar4,0x49,&local_30);
    }
    else if (uVar1 == 10) {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        local_3c = DAT_004437a8;
        local_40 = 499;
        FUN_0043d574(2,DAT_00443760,DAT_0044375c,DAT_00443758);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_004437ac,DAT_004437ac);
      }
    }
    else if (uVar1 < 10) {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        local_38 = local_30;
        local_3c = DAT_00443798;
        local_40 = 0x1e9;
        FUN_0043d574(3,DAT_00443760,DAT_0044375c,DAT_00443758);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_0044379c,DAT_0044379c,local_30);
      }
      FUN_0045f8fc(*puVar4,0x41,&local_30);
    }
    else if (uVar1 == 0xc) {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        local_38 = local_30;
        local_3c = DAT_004437c0;
        local_40 = 0x202;
        FUN_0043d574(4,DAT_00443760,DAT_0044375c,DAT_00443758);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004437c4,DAT_004437c4,local_30);
      }
      settings_role_head_up_profile(local_30);
      FUN_0046c9aa();
    }
    else if (uVar1 < 0xc) {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        local_38 = local_30;
        local_3c = DAT_004437b8;
        local_40 = 0x1fc;
        FUN_0043d574(4,DAT_00443760,DAT_0044375c,DAT_00443758);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004437bc,DAT_004437bc,local_30);
      }
      system_get_brightness_level(local_30);
      FUN_0046c984();
    }
    else if (uVar1 == 0xe) {
      uVar2 = param_1[3];
      uVar3 = param_1[4];
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        local_34 = (int)(short)uVar3;
        local_38 = (uint)(short)uVar2;
        local_3c = DAT_00443788;
        local_40 = 0x1d3;
        FUN_0043d574(4,DAT_00443760,DAT_0044375c,DAT_00443758);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        local_40 = (int)(short)uVar3;
        compress_log_output(0x10800000,DAT_0044378c,DAT_0044378c,(int)(short)uVar2);
      }
      local_28 = (int)(short)uVar2;
      local_24 = (int)(short)uVar3;
      FUN_0045f8fc(*puVar4,0x4a,&local_28);
    }
    else if (0xd < uVar1) {
      if (uVar1 == 0x10) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          local_38 = local_30;
          local_3c = DAT_004437a0;
          local_40 = 0x1ee;
          FUN_0043d574(3,DAT_00443760,DAT_0044375c,DAT_00443758);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_004437a4,DAT_004437a4,local_30);
        }
        FUN_0045f8fc(*puVar4,0x50,&local_30);
      }
      else if (uVar1 < 0x10) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          local_38 = local_30;
          local_3c = DAT_004437b0;
          local_40 = 0x1f7;
          FUN_0043d574(3,DAT_00443760,DAT_0044375c,DAT_00443758);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_004437b4,DAT_004437b4,local_30);
        }
        FUN_0045f8fc(*puVar4,0x4f,&local_30);
      }
      else {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          local_3c = DAT_004437c8;
          local_40 = 0x20b;
          local_38 = uVar1;
          FUN_0043d574(2,DAT_00443760,DAT_0044375c,DAT_00443758);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_004437cc,DAT_004437cc,uVar1);
        }
      }
    }
    uVar8 = 0;
  }
  return uVar8;
}

