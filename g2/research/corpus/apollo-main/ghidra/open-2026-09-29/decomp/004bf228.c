
undefined4 _anccAttrHandler(undefined1 *param_1,ushort param_2)

{
  undefined1 uVar1;
  undefined1 uVar2;
  byte bVar3;
  ushort uVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  int iVar8;
  ushort uVar9;
  byte bVar10;
  
  iVar8 = DAT_004bf6c0;
  bVar10 = 0;
  bVar3 = *(byte *)(DAT_004bf6c0 + 10);
  if (bVar3 == 0) {
    *(undefined1 *)(DAT_004bf6c0 + 0x16) = *param_1;
    if (*(char *)(iVar8 + 0x16) == '\0') {
      *(uint *)(iVar8 + 0x18) =
           (uint)(byte)param_1[2] * 0x100 + (uint)(byte)param_1[1] +
           (uint)(byte)param_1[3] * 0x10000 + (uint)(byte)param_1[4] * 0x1000000;
      bVar10 = 4;
    }
    else {
      if (*(char *)(iVar8 + 0x16) != '\x01') {
        return 0;
      }
      while (param_1[bVar10 + 1] != '\0') {
        *(undefined1 *)((uint)bVar10 + iVar8 + 0x31c) = param_1[bVar10 + 1];
        bVar10 = bVar10 + 1;
      }
      *(undefined1 *)((uint)bVar10 + iVar8 + 0x31d) = 0;
      iVar7 = DAT_004bf900;
      if (param_1[bVar10 + 2] == '\0') {
        uVar2 = param_1[bVar10 + 3];
        uVar1 = param_1[bVar10 + 4];
        iVar8 = DAT_004bf900 + 0x48;
        FUN_0043c0e4(iVar8,0x20,0);
        FUN_00439be4(iVar8,param_1 + bVar10 + 5,CONCAT11(uVar1,uVar2));
        *(undefined1 *)(iVar7 + (uint)CONCAT11(uVar1,uVar2) + 0x48) = 0;
        if ((*(char *)(iVar7 + 5) == '\0') || (*(char *)(iVar7 + 5) == '\x01')) {
          bVar3 = SVC_IsOnWhitelistByIdentifier(iVar7 + 8);
        }
        else {
          bVar3 = 2;
        }
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004bf92c,DAT_004bf928,DAT_004bf924,0x256,DAT_004bf920,bVar3);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_004bf930,DAT_004bf930,bVar3);
        }
        if (bVar3 == 1) {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(3,DAT_004bf92c,DAT_004bf928,DAT_004bf924,0x263,DAT_004bf94c,iVar7 + 8,iVar8
                        );
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0xc800000,DAT_004bf950,DAT_004bf950,iVar7 + 8,iVar8);
          }
          APP_PbTxEncodeNotifAppIDNotInWhitelist(iVar7 + 8,iVar8);
          FUN_0043c0e4(iVar7,0x2fc,0);
          _anccResetStateMachine();
          return 0;
        }
        if (bVar3 != 0) {
          if (bVar3 == 3) {
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              FUN_0043d574(3,DAT_004bf92c,DAT_004bf928,DAT_004bf924,0x25e,DAT_004bf944,iVar7 + 8,
                           iVar8);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0xc800000,DAT_004bf948,DAT_004bf948,iVar7 + 8,iVar8);
            }
          }
          else {
            if (2 < bVar3) goto LAB_004bf52e;
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              FUN_0043d574(3,DAT_004bf92c,DAT_004bf928,DAT_004bf924,0x259,DAT_004bf934,iVar7 + 8,
                           iVar8);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0xc800000,DAT_004bf938,DAT_004bf938,iVar7 + 8,iVar8);
            }
          }
          _anccSendCompleteNotificationMsg(iVar7,0x2fc);
          FUN_0043c0e4(iVar7,0x2fc,0);
          iVar8 = FUN_0043d0ce();
          if (iVar8 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004bf92c,DAT_004bf928,DAT_004bf924,0x279,DAT_004bf93c);
          }
          iVar8 = FUN_0043d0ce();
          if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_004bf940,DAT_004bf940);
          }
          _anccResetStateMachine();
          return 0;
        }
LAB_004bf52e:
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004bf92c,DAT_004bf928,DAT_004bf924,0x26c,DAT_004bf954,iVar7 + 8,iVar8);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0xc800000,DAT_004bf958,DAT_004bf958,iVar7 + 8,iVar8);
        }
        _anccResetStateMachine();
        return 0;
      }
    }
    *(ushort *)(iVar8 + 0xe) = *(short *)(iVar8 + 0xe) + (ushort)bVar10 + 1;
    *(undefined1 *)(iVar8 + 10) = 1;
    *(undefined1 *)(iVar8 + 0x12) = 0;
    *(undefined2 *)(iVar8 + 0x14) = 0;
    uVar9 = 0;
    if (param_2 < 0x201) {
      uVar9 = param_2;
    }
    FUN_0043c0e4(iVar8 + 0x35c,0x200,0);
    *(undefined2 *)(iVar8 + 0xc) = 0;
    for (uVar4 = 0; uVar4 < uVar9; uVar4 = uVar4 + 1) {
      *(undefined1 *)((uint)*(ushort *)(iVar8 + 0xc) + iVar8 + 0x35c) = param_1[uVar4];
      *(short *)(iVar8 + 0xc) = *(short *)(iVar8 + 0xc) + 1;
    }
  }
  else {
    if (bVar3 == 2) {
      if (0x200 < (uint)*(ushort *)(DAT_004bf6c0 + 0xc) + (uint)param_2) {
        *(undefined1 *)(DAT_004bf6c0 + 10) = 0;
        *(undefined2 *)(iVar8 + 0xe) = 0;
        *(undefined2 *)(iVar8 + 0xc) = 0;
        return 0;
      }
      for (uVar9 = 0; uVar9 < param_2; uVar9 = uVar9 + 1) {
        *(undefined1 *)((uint)*(ushort *)(iVar8 + 0xc) + iVar8 + 0x35c) = param_1[uVar9];
        *(short *)(iVar8 + 0xc) = *(short *)(iVar8 + 0xc) + 1;
      }
      *(undefined1 *)(iVar8 + 10) = 1;
      return 1;
    }
    if (1 < bVar3) {
      return 0;
    }
  }
  if ((int)((uint)*(ushort *)(iVar8 + 0xc) - (uint)*(ushort *)(iVar8 + 0xe)) < 3) {
    *(undefined1 *)(iVar8 + 10) = 2;
    uVar6 = 0;
  }
  else {
    *(undefined1 *)(iVar8 + 0x12) = *(undefined1 *)((uint)*(ushort *)(iVar8 + 0xe) + iVar8 + 0x35c);
    *(ushort *)(iVar8 + 0x10) =
         (ushort)*(byte *)((uint)*(ushort *)(iVar8 + 0xe) + iVar8 + 0x35e) * 0x100 +
         (ushort)*(byte *)((uint)*(ushort *)(iVar8 + 0xe) + iVar8 + 0x35d);
    if ((int)(((uint)*(ushort *)(iVar8 + 0xc) - (uint)*(ushort *)(iVar8 + 0xe)) + -3) <
        (int)(uint)*(ushort *)(iVar8 + 0x10)) {
      *(undefined1 *)(iVar8 + 10) = 2;
      uVar6 = 0;
    }
    else {
      *(short *)(iVar8 + 0x14) = *(short *)(iVar8 + 0x14) + 1;
      *(short *)(iVar8 + 0xe) = *(short *)(iVar8 + 0xe) + 3;
      _ancsAnccAttrCback(iVar8 + 8);
      *(short *)(iVar8 + 0xe) = *(short *)(iVar8 + 0x10) + *(short *)(iVar8 + 0xe);
      if (*(ushort *)(iVar8 + 0x14) < 8) {
        uVar6 = 1;
      }
      else {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004bf92c,DAT_004bf928,DAT_004bf924,0x2bd,DAT_004bf95c);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004bf960,DAT_004bf960);
        }
        _anccResetStateMachine();
        AncsPerformNotiAction(*(undefined4 *)(iVar8 + 4),*(undefined4 *)(iVar8 + 0x18),1);
        uVar6 = 0;
      }
    }
  }
  return uVar6;
}

