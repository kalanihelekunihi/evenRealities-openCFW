
undefined8 FUN_00532924(byte *param_1,undefined4 param_2)

{
  byte bVar1;
  undefined1 uVar2;
  char cVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  int *piVar8;
  byte *pbVar9;
  
  iVar4 = DAT_0053345c + (uint)*param_1 * 0x10;
  piVar8 = (int *)(iVar4 + -0x10);
  pbVar9 = param_1;
  if (param_1[3] == 0x12) {
    FUN_00531f20((char)*(undefined2 *)param_1);
  }
  if (*(char *)(iVar4 + -5) == '\x03') {
    if (param_1[2] == 4) {
      bVar1 = (byte)*(undefined2 *)param_1;
      if (param_1[3] == 0) {
        *(undefined1 *)(iVar4 + -5) = 0;
        iVar5 = FUN_004bb07c(bVar1);
        if (iVar5 == 0) {
          if (bVar1 == 0) {
            iVar4 = FUN_004c9c50();
            if ((iVar4 == 0) || (iVar4 = FUN_0044b610(DAT_00533464,&DAT_00532cc0,3), iVar4 != 0)) {
              iVar4 = FUN_004c9c50();
              if ((iVar4 == 0) || (iVar4 = FUN_0044b610(DAT_00533464,DAT_00533464,4), iVar4 != 0)) {
                iVar4 = FUN_004c9c50();
                if ((iVar4 == 0) || (iVar4 = FUN_0044b610(DAT_00533464,DAT_00533470,4), iVar4 != 0))
                {
                  iVar4 = FUN_004c9c50();
                  if (iVar4 == 0) {
                    iVar4 = FUN_004c9c50();
                    if ((iVar4 == 0) ||
                       (iVar4 = FUN_0044b610(&DAT_00532cc4,&DAT_00532cc8,3), iVar4 != 0)) {
                      WsfTrace(DAT_00533464,DAT_00533468,0);
                    }
                  }
                  else {
                    iVar4 = FUN_0043d0ce();
                    if (iVar4 << 0x1e < 0) {
                      pbVar9 = (byte *)0x29e;
                      param_2 = DAT_00533468;
                      FUN_0043d574(4,&DAT_00532cc4,DAT_0053302c,DAT_0053346c,0x29e,DAT_00533468,0);
                    }
                  }
                }
                else {
                  iVar4 = FUN_0043d0ce();
                  if (iVar4 << 0x1e < 0) {
                    pbVar9 = (byte *)0x29e;
                    param_2 = DAT_00533468;
                    FUN_0043d574(3,&DAT_00532cc4,DAT_0053302c,DAT_0053346c,0x29e,DAT_00533468,0);
                  }
                }
              }
              else {
                iVar4 = FUN_0043d0ce();
                if (iVar4 << 0x1e < 0) {
                  pbVar9 = (byte *)0x29e;
                  param_2 = DAT_00533468;
                  FUN_0043d574(2,&DAT_00532cc4,DAT_0053302c,DAT_0053346c,0x29e,DAT_00533468,0);
                }
              }
            }
            else {
              iVar4 = FUN_0043d0ce();
              if (iVar4 << 0x1e < 0) {
                pbVar9 = (byte *)0x29e;
                param_2 = DAT_00533468;
                FUN_0043d574(1,&DAT_00532cc4,DAT_0053302c,DAT_0053346c,0x29e,DAT_00533468,0);
              }
            }
            goto LAB_00532e4e;
          }
          iVar5 = DmConnRole(bVar1);
          uVar6 = DmConnPeerAddr(bVar1);
          uVar2 = DmConnPeerAddrType(bVar1);
          iVar5 = FUN_0047a71c(uVar2,uVar6,iVar5 == 0);
          *(int *)(DAT_0053362c + (uint)bVar1 * 0x30 + -0x30) = iVar5;
        }
        iVar7 = FUN_004751c8(iVar5 + 0x87,*(int *)(param_1 + 4) + 3,0x10);
        if (iVar7 == 0) {
          FUN_00439be4(*(undefined4 *)(iVar4 + -0xc),iVar5 + 0x98,(uint)*(byte *)(iVar4 + -6) << 1);
          FUN_00531bd4(bVar1,*(undefined1 *)(iVar5 + 0xc2));
        }
        else {
          FUN_0047b3ae(iVar5,*(int *)(param_1 + 4) + 3);
          FUN_0047b3cc(iVar5,1);
          (*(code *)*DAT_00533624)(bVar1,3);
        }
      }
      else {
        (*(code *)*DAT_00533624)(bVar1,3);
      }
    }
  }
  else if (*(char *)(iVar4 + -5) == '\x01') {
    if (param_1[2] == 3) {
      cVar3 = AttcDiscServiceCmpl(*piVar8,param_1);
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        pbVar9 = (byte *)0x2d1;
        param_2 = DAT_005336c8;
        FUN_0043d574(4,DAT_00532e8c,DAT_0053302c,DAT_0053346c,0x2d1,DAT_005336c8,cVar3);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_005336cc,DAT_005336cc,cVar3);
      }
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        pbVar9 = (byte *)0x2d2;
        param_2 = DAT_005336d0;
        FUN_0043d574(4,DAT_00532e8c,DAT_0053302c,DAT_0053346c,0x2d2,DAT_005336d0,
                     *(undefined2 *)(*piVar8 + 0xe),*(undefined2 *)(*piVar8 + 0x10));
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        pbVar9 = (byte *)(uint)*(ushort *)(*piVar8 + 0x10);
        compress_log_output(0x10800000,DAT_005336d4,DAT_005336d4,*(undefined2 *)(*piVar8 + 0xe));
      }
      if (cVar3 == '\0') {
        AttcDiscCharStart((char)*(undefined2 *)param_1,*piVar8);
      }
      else if (cVar3 != 'y') {
        DmConnSetIdle((char)*(undefined2 *)param_1,8,0);
        (*(code *)*DAT_00533624)((char)*(undefined2 *)param_1,5);
      }
    }
    else if ((param_1[2] == 4) || (param_1[2] == 2)) {
      cVar3 = AttcDiscCharCmpl(*piVar8,param_1);
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        pbVar9 = (byte *)0x2ea;
        param_2 = DAT_005336d8;
        FUN_0043d574(4,DAT_00532e8c,DAT_0053302c,DAT_0053346c,0x2ea,DAT_005336d8,cVar3);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_005336dc,DAT_005336dc,cVar3);
      }
      if (param_1[2] == 4) {
        if (7 < *(ushort *)(param_1 + 8)) {
          FUN_005322f6(*piVar8,param_1);
        }
      }
      else if (4 < *(ushort *)(param_1 + 8)) {
        FUN_00532644(*piVar8,param_1);
      }
      if (cVar3 == '\0') {
        (*(code *)*DAT_00533624)((char)*(undefined2 *)param_1,4);
      }
      else if (cVar3 != 'y') {
        DmConnSetIdle((char)*(undefined2 *)param_1,8,0);
        (*(code *)*DAT_00533624)((char)*(undefined2 *)param_1,5);
      }
    }
  }
  else if ((*(char *)(iVar4 + -5) == '\x02') && ((param_1[2] == 5 || (param_1[2] == 9)))) {
    if (*(char *)(iVar4 + -2) == '\0') {
      if (((param_1[3] == 5) || (param_1[3] == 0xf)) &&
         (iVar5 = DmConnSecLevel((char)*(undefined2 *)param_1), iVar5 == 0)) {
        *(undefined1 *)(iVar4 + -3) = 1;
        (*(code *)*DAT_00533624)((char)*(undefined2 *)param_1,2);
      }
      else {
        cVar3 = AttcDiscConfigCmpl((char)*(undefined2 *)param_1,*piVar8);
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          pbVar9 = (byte *)0x322;
          param_2 = DAT_0053384c;
          FUN_0043d574(4,DAT_00532e8c,DAT_0053302c,DAT_0053346c,0x322,DAT_0053384c,cVar3);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_00533850,DAT_00533850,cVar3);
        }
        if (cVar3 != 'y') {
          (*(code *)*DAT_00533624)((char)*(undefined2 *)param_1,8);
        }
      }
    }
    else {
      *(undefined1 *)(iVar4 + -2) = 0;
      *(undefined1 *)(iVar4 + -5) = 0;
      FUN_00531d60((char)*(undefined2 *)param_1);
    }
  }
  else if ((*(char *)(iVar4 + -5) == '\x02') && ((param_1[3] != 0 && (param_1[3] != 0x79)))) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      pbVar9 = (byte *)0x330;
      param_2 = DAT_00533854;
      FUN_0043d574(2,DAT_00532e8c,DAT_0053302c,DAT_0053346c,0x330,DAT_00533854,param_1[3]);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_00533858,DAT_00533858,param_1[3]);
    }
    DmConnSetIdle((char)*(undefined2 *)param_1,8,0);
    *(undefined1 *)(iVar4 + -5) = 0;
    (*(code *)*DAT_00533624)((char)*(undefined2 *)param_1,5);
  }
LAB_00532e4e:
  return CONCAT44(param_2,pbVar9);
}

