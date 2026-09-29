
void _bleMasterScanReport(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  int *piVar2;
  undefined4 uVar3;
  undefined1 uVar4;
  byte *pbVar5;
  int iVar6;
  int iVar7;
  undefined1 auStack_34 [32];
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  FUN_0043c0e4(auStack_34,0x20,0);
  bVar1 = false;
  if (*(char *)(*DAT_004a0518 + 0x58) != '\0') {
    pbVar5 = (byte *)DmFindAdType(9,*(undefined1 *)(param_1 + 8),*(undefined4 *)(param_1 + 4));
    if (pbVar5 == (byte *)0x0) {
      pbVar5 = (byte *)DmFindAdType(8,*(undefined1 *)(param_1 + 8),*(undefined4 *)(param_1 + 4));
      if (pbVar5 != (byte *)0x0) {
        FUN_00439be4(auStack_34,pbVar5 + 2,*pbVar5 - 1);
      }
    }
    else {
      FUN_00439be4(auStack_34,pbVar5 + 2,*pbVar5 - 1);
    }
    uVar3 = DAT_004a062c;
    if (*DAT_004a0604 == '\x04') {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        uVar4 = DmHostAddrType(*(undefined1 *)(param_1 + 0xb));
        FUN_0043d574(4,DAT_004a02d8,DAT_004a02d4,DAT_004a0624,0x162,DAT_004a0620,
                     *(undefined1 *)(param_1 + 0x11),*(undefined1 *)(param_1 + 0x10),
                     *(undefined1 *)(param_1 + 0xf),*(undefined1 *)(param_1 + 0xe),
                     *(undefined1 *)(param_1 + 0xd),*(undefined1 *)(param_1 + 0xc),
                     (int)*(char *)(param_1 + 9),auStack_34,uVar4);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        uVar4 = DmHostAddrType(*(undefined1 *)(param_1 + 0xb));
        compress_log_output(0x12400000,DAT_004a0628,DAT_004a0628,*(undefined1 *)(param_1 + 0x11),
                            *(undefined1 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0xf),
                            *(undefined1 *)(param_1 + 0xe),*(undefined1 *)(param_1 + 0xd),
                            *(undefined1 *)(param_1 + 0xc),(int)*(char *)(param_1 + 9),auStack_34,
                            uVar4);
      }
    }
    else {
      iVar6 = FUN_004751c8(param_1 + 0xc,DAT_004a062c,6);
      if (iVar6 == 0) {
        FUN_0043dacc(DAT_004a0630,0x10,*(undefined4 *)(param_1 + 4),*(undefined1 *)(param_1 + 8));
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          uVar4 = DmHostAddrType(*(undefined1 *)(param_1 + 0xb));
          FUN_0043d574(4,DAT_004a02d8,DAT_004a02d4,DAT_004a0624,0x170,DAT_004a0620,
                       *(undefined1 *)(param_1 + 0x11),*(undefined1 *)(param_1 + 0x10),
                       *(undefined1 *)(param_1 + 0xf),*(undefined1 *)(param_1 + 0xe),
                       *(undefined1 *)(param_1 + 0xd),*(undefined1 *)(param_1 + 0xc),
                       (int)*(char *)(param_1 + 9),auStack_34,uVar4);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          uVar4 = DmHostAddrType(*(undefined1 *)(param_1 + 0xb));
          compress_log_output(0x12400000,DAT_004a0628,DAT_004a0628,*(undefined1 *)(param_1 + 0x11),
                              *(undefined1 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0xf),
                              *(undefined1 *)(param_1 + 0xe),*(undefined1 *)(param_1 + 0xd),
                              *(undefined1 *)(param_1 + 0xc),(int)*(char *)(param_1 + 9),auStack_34,
                              uVar4);
        }
        bVar1 = true;
      }
      iVar6 = FUN_004751c8(param_1 + 0xc,uVar3,6);
      if (iVar6 == 0) {
        iVar6 = FUN_0047ad74(*(undefined1 *)(param_1 + 0xb),param_1 + 0xc);
        if (iVar6 == 0) {
          if ((*(char *)(param_1 + 0xb) == '\x01') && ((*(byte *)(param_1 + 0x11) & 0xc0) == 0x40))
          {
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              FUN_0043d574(3,DAT_004a02d8,DAT_004a02d4,DAT_004a0624,0x18d,DAT_004a0644,
                           *(undefined1 *)(param_1 + 0x11),*(undefined1 *)(param_1 + 0x10),
                           *(undefined1 *)(param_1 + 0xf),*(undefined1 *)(param_1 + 0xe),
                           *(undefined1 *)(param_1 + 0xd),*(undefined1 *)(param_1 + 0xc));
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0xd800000,DAT_004a0648,DAT_004a0648,
                                  *(undefined1 *)(param_1 + 0x11),*(undefined1 *)(param_1 + 0x10),
                                  *(undefined1 *)(param_1 + 0xf),*(undefined1 *)(param_1 + 0xe),
                                  *(undefined1 *)(param_1 + 0xd),*(undefined1 *)(param_1 + 0xc));
            }
            iVar7 = FUN_0047a8c4(*(undefined1 *)(param_1 + 0xb),param_1 + 0xc);
            if (iVar7 != 0) {
              iVar6 = FUN_0043d0ce();
              if (iVar6 << 0x1e < 0) {
                FUN_0043d574(4,DAT_004a02d8,DAT_004a02d4,DAT_004a0624,0x192,DAT_004a064c);
              }
              iVar6 = FUN_0043d0ce();
              if ((-1 < iVar6 << 0x1f) && (iVar6 = FUN_0043d0ce(), -1 < iVar6 << 0x1d)) {
                return;
              }
              compress_log_output(0x10000000,DAT_004a0650,DAT_004a0650);
              return;
            }
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              FUN_0043d574(2,DAT_004a02d8,DAT_004a02d4,DAT_004a0624,0x198,DAT_004a0654);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0x8000000,DAT_004a0658,DAT_004a0658);
            }
          }
          else {
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              FUN_0043d574(4,DAT_004a02d8,DAT_004a02d4,DAT_004a0624,0x1a0,DAT_004a065c,
                           *(undefined1 *)(param_1 + 0x11),*(undefined1 *)(param_1 + 0x10),
                           *(undefined1 *)(param_1 + 0xf),*(undefined1 *)(param_1 + 0xe),
                           *(undefined1 *)(param_1 + 0xd),*(undefined1 *)(param_1 + 0xc));
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0x11800000,DAT_004a0660,DAT_004a0660,
                                  *(undefined1 *)(param_1 + 0x11),*(undefined1 *)(param_1 + 0x10),
                                  *(undefined1 *)(param_1 + 0xf),*(undefined1 *)(param_1 + 0xe),
                                  *(undefined1 *)(param_1 + 0xd),*(undefined1 *)(param_1 + 0xc));
            }
            iVar7 = FUN_0047a8c4(*(undefined1 *)(param_1 + 0xb),param_1 + 0xc);
            if (iVar7 != 0) {
              iVar7 = FUN_0043d0ce();
              if (iVar7 << 0x1e < 0) {
                FUN_0043d574(4,DAT_004a02d8,DAT_004a02d4,DAT_004a0624,0x1a4,DAT_004a0664);
              }
              iVar7 = FUN_0043d0ce();
              if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
                compress_log_output(0x10000000,DAT_004a0668,DAT_004a0668);
              }
            }
            bVar1 = true;
          }
        }
        else {
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            FUN_0043d574(3,DAT_004a02d8,DAT_004a02d4,DAT_004a0624,0x17b,DAT_004a0634,
                         *(undefined1 *)(param_1 + 0x11),*(undefined1 *)(param_1 + 0x10),
                         *(undefined1 *)(param_1 + 0xf),*(undefined1 *)(param_1 + 0xe),
                         *(undefined1 *)(param_1 + 0xd),*(undefined1 *)(param_1 + 0xc));
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            compress_log_output(0xd800000,DAT_004a0638,DAT_004a0638,*(undefined1 *)(param_1 + 0x11),
                                *(undefined1 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0xf),
                                *(undefined1 *)(param_1 + 0xe),*(undefined1 *)(param_1 + 0xd),
                                *(undefined1 *)(param_1 + 0xc));
          }
          if ((*(char *)(param_1 + 0x12) == '\x01') && ((*(byte *)(param_1 + 0x18) & 0xc0) == 0x40))
          {
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              FUN_0043d574(4,DAT_004a02d8,DAT_004a02d4,DAT_004a0624,0x180,DAT_004a063c);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0x10000000,DAT_004a0640,DAT_004a0640);
            }
            FUN_00503ffc(param_1,iVar6,1);
          }
          else {
            bVar1 = true;
          }
        }
        if (bVar1) {
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004a02d8,DAT_004a02d4,DAT_004a0624,0x1ab,DAT_004a066c,
                         (int)*(char *)(param_1 + 9));
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_004a0670,DAT_004a0670,(int)*(char *)(param_1 + 9));
          }
          piVar2 = DAT_004a05e8;
          if (*(char *)(*DAT_004a05e8 + 0x16) < *(char *)(param_1 + 9)) {
            *(undefined1 *)(*DAT_004a05e8 + 0x16) = *(undefined1 *)(param_1 + 9);
            uVar4 = DmHostAddrType(*(undefined1 *)(param_1 + 0xb));
            *(undefined1 *)(*piVar2 + 8) = uVar4;
            FUN_00439be4(*piVar2 + 9,param_1 + 0xc,6);
            *(int *)(*piVar2 + 4) = iVar6;
            *(undefined1 *)(*piVar2 + 0x15) = 1;
            AppScanStop();
          }
        }
      }
    }
  }
  return;
}

