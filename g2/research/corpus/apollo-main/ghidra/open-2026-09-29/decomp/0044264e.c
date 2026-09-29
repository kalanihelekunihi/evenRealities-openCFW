
undefined4 FUN_0044264e(uint param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  char cVar4;
  int iVar5;
  undefined4 uVar6;
  uint *puVar7;
  uint uVar8;
  undefined4 uVar9;
  int iVar10;
  uint *puVar11;
  undefined4 local_2c;
  undefined1 local_28;
  undefined1 local_27;
  undefined4 uStack_20;
  
  uStack_20 = param_4;
  iVar5 = FUN_0045bbf4();
  puVar1 = DAT_00442cdc;
  if (iVar5 == 1) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00442cf4,DAT_00442cf0,DAT_00442d2c,0xbc,DAT_00442d28,param_1);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_00442d30,DAT_00442d30,param_1);
    }
    uVar6 = 0xffffffff;
  }
  else {
    puVar7 = (uint *)FUN_0045f8d0(*DAT_00442cdc);
    if ((puVar7 == (uint *)0x0) || (*puVar7 == param_1)) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00442cf4,DAT_00442cf0,DAT_00442d2c,0xc1,DAT_00442d34,param_1);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_00442d38,DAT_00442d38,param_1);
      }
      if (puVar7 == (uint *)0x0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00442cf4,DAT_00442cf0,DAT_00442d2c,0xc5,DAT_00442d44);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_00442d48,DAT_00442d48);
        }
      }
      else {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00442cf4,DAT_00442cf0,DAT_00442d2c,0xc3,DAT_00442d3c,*puVar7);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_00442d40,DAT_00442d40,*puVar7);
        }
      }
      uVar6 = 0xffffffff;
    }
    else {
      cVar4 = FUN_00442618(param_1);
      if (cVar4 == '\x02') {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(2,DAT_00442cf4,DAT_00442cf0,DAT_00442d2c,0xcb,DAT_00442d4c,param_1);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_00442d50,DAT_00442d50,param_1);
        }
        uVar6 = 0xffffffff;
      }
      else {
        if (*(char *)((int)puVar7 + 0xb) == '\0') {
          if (cVar4 == '\x01') {
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              local_2c = 1;
              FUN_0043d574(4,DAT_00442cf4,DAT_00442cf0,DAT_00442d2c,0xd0,DAT_00442d54,param_1);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0x10800000,DAT_00442d58,DAT_00442d58,param_1,1);
            }
            if (param_1 == 3) {
              iVar5 = FUN_0043d0ce();
              if (iVar5 << 0x1e < 0) {
                FUN_0043d574(4,DAT_00442cf4,DAT_00442cf0,DAT_00442d2c,0xd2,DAT_00442d5c);
              }
              iVar5 = FUN_0043d0ce();
              if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                compress_log_output(0x10000000,DAT_00442d60,DAT_00442d60);
              }
              FUN_0043c0e4(&local_2c,10,0);
              FUN_0043c0e4(&local_2c,10,0);
              uVar3 = DAT_004434b0;
              uVar2 = DAT_004434ac;
              uVar9 = DAT_00443498;
              uVar6 = DAT_00443480;
              local_2c = CONCAT22(local_2c._2_2_,0xf001);
              uVar8 = *puVar7;
              if (uVar8 == 1) {
                iVar5 = 0;
              }
              else if (uVar8 == 5) {
                uVar6 = FUN_00460084(DAT_00443498);
                FUN_0045fffe(uVar9,uVar6);
                iVar5 = FUN_004628c4();
              }
              else if (uVar8 == 6) {
                uVar6 = FUN_00460084(DAT_004434ac);
                FUN_0045fffe(uVar2,uVar6);
                iVar5 = FUN_004628c4();
              }
              else if (uVar8 == 8) {
                uVar6 = FUN_00460084(DAT_004434b0);
                FUN_0045fffe(uVar3,uVar6);
                iVar5 = FUN_004628c4();
              }
              else if (uVar8 == 0xb) {
                uVar9 = FUN_00460084(DAT_00443480);
                FUN_0045fffe(uVar6,uVar9);
                iVar5 = FUN_004628c4();
              }
              else {
                iVar5 = -1;
              }
              if (iVar5 < 0) {
                local_2c._0_3_ = (uint3)local_2c & 0xffff;
                local_2c = (uint)(uint3)local_2c;
                local_28 = 0;
                local_27 = 0;
                iVar5 = FUN_0043d0ce();
                if (iVar5 << 0x1e < 0) {
                  FUN_0043d574(4,DAT_00442cf4,DAT_00442cf0,DAT_00442d2c,0xfa,DAT_004434ec);
                }
                iVar5 = FUN_0043d0ce();
                if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                  compress_log_output(0x10000000,DAT_004434f0,DAT_004434f0);
                }
                FUN_0044228a(3,3,&local_2c,6);
              }
              else {
                iVar10 = FUN_0043d0ce();
                if (iVar10 << 0x1e < 0) {
                  FUN_0043d574(4,DAT_00442cf4,DAT_00442cf0,DAT_00442d2c,0xee,DAT_004434cc,iVar5);
                }
                iVar10 = FUN_0043d0ce();
                if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
                  compress_log_output(0x10400000,DAT_004434e8,DAT_004434e8,iVar5);
                }
                local_2c._0_3_ = CONCAT12((char)iVar5,(undefined2)local_2c);
                local_2c = CONCAT13((char)((uint)iVar5 >> 8),(uint3)local_2c);
                local_28 = (undefined1)((uint)iVar5 >> 0x10);
                local_27 = (undefined1)((uint)iVar5 >> 0x18);
                FUN_0044228a(3,3,&local_2c,6);
              }
            }
            cVar4 = FUN_0045faa8(*puVar1,1,param_1);
            if (cVar4 == '\x01') {
              iVar5 = FUN_0043d0ce();
              if (iVar5 << 0x1e < 0) {
                FUN_0043d574(4,DAT_00442cf4,DAT_00442cf0,DAT_00442d2c,0x100,DAT_004434f4);
              }
              iVar5 = FUN_0043d0ce();
              if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                compress_log_output(0x10000000,DAT_004434f8,DAT_004434f8);
              }
              *DAT_00442ce4 = param_1;
              return 1;
            }
          }
          else if (cVar4 == '\0') {
            puVar11 = (uint *)FUN_0045f6a8(*puVar1);
            if (*puVar11 != param_1) {
              FUN_00464242(puVar11[1],300);
              for (iVar5 = 0; iVar5 < 0x16; iVar5 = iVar5 + 1) {
                FUN_00464344();
                FUN_00454b4c(0x10);
              }
            }
            iVar5 = FUN_0045a568();
            if ((iVar5 == 1) && (*puVar11 != param_1)) {
              FUN_00464c36(*puVar7 & 0xffff,0,0,0);
              FUN_00464b2e(param_1 & 0xffff,param_2,param_3 & 0xffff,0);
            }
          }
        }
        else if (*(char *)((int)puVar7 + 0xb) == '\x01') {
          if (cVar4 == '\0') {
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              local_2c = 0;
              FUN_0043d574(4,DAT_00442cf4,DAT_00442cf0,DAT_00442d2c,0x115,DAT_004434fc,param_1);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0x10800000,DAT_00443500,DAT_00443500,param_1,0);
            }
            iVar5 = FUN_0045a568();
            if (iVar5 == 1) {
              FUN_00464c36(*puVar7 & 0xffff,0,0,0);
              FUN_0045a8ee(param_1,param_2,param_3,500);
            }
          }
          else if (cVar4 == '\x01') {
            uVar6 = FUN_0045f840(*puVar1,param_1);
            iVar5 = FUN_0045f706(*puVar1,uVar6);
            if (iVar5 == 1) {
              FUN_0044228a(*puVar7,5,0,0);
            }
            cVar4 = FUN_0045faa8(*puVar1,2,param_1);
            if (cVar4 == '\x01') {
              uVar6 = FUN_0045f840(*puVar1,param_1);
              iVar5 = FUN_0045f706(*puVar1,uVar6);
              if (iVar5 == 1) {
                *DAT_00442ce4 = param_1;
                return 1;
              }
            }
          }
        }
        uVar6 = 0;
      }
    }
  }
  return uVar6;
}

