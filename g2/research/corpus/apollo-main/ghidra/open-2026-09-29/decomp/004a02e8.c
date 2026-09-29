
void _masterConnect(int param_1)

{
  int *piVar1;
  undefined4 uVar2;
  char cVar3;
  int iVar4;
  int iVar5;
  
  if (param_1 << 0x1f < 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004a0fd0,DAT_004a0fcc,DAT_004a068c,0x1d0,DAT_004a0688);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004a0690,DAT_004a0690);
    }
    if (*DAT_004a0fd4 == '\x01') {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(3,DAT_004a0fd0,DAT_004a0fcc,DAT_004a068c,0x1d6,DAT_004a0694);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004a0698);
      }
    }
    else {
      _SetRingLinkState(1,DAT_004a069c);
      piVar1 = DAT_004a05e8;
      *(undefined1 *)(*DAT_004a05e8 + 8) = 1;
      FUN_00439be4(*piVar1 + 9,DAT_004a062c,6);
      iVar4 = FUN_0047ad74(*(undefined1 *)(*piVar1 + 8),*piVar1 + 9);
      if (iVar4 != 0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004a0fd0,DAT_004a0fcc,DAT_004a068c,0x1e1,DAT_004a06a0,
                       *(undefined1 *)(*piVar1 + 0xe),*(undefined1 *)(*piVar1 + 0xd),
                       *(undefined1 *)(*piVar1 + 0xc),*(undefined1 *)(*piVar1 + 0xb),
                       *(undefined1 *)(*piVar1 + 10),*(undefined1 *)(*piVar1 + 9));
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0xd800000,DAT_004a06a4,DAT_004a06a4,*(undefined1 *)(*piVar1 + 0xe),
                              *(undefined1 *)(*piVar1 + 0xd),*(undefined1 *)(*piVar1 + 0xc),
                              *(undefined1 *)(*piVar1 + 0xb),*(undefined1 *)(*piVar1 + 10),
                              *(undefined1 *)(*piVar1 + 9));
        }
      }
      *(int *)(*piVar1 + 4) = iVar4;
      DmConnSetScanInterval(*DAT_004a05e4,DAT_004a05e4[1]);
      *DAT_004a1160 = 0;
      *DAT_004a1164 = 0;
      cVar3 = AppConnOpen(*(undefined1 *)(*piVar1 + 8),*piVar1 + 9,*(undefined4 *)(*piVar1 + 4));
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004a0fd0,DAT_004a0fcc,DAT_004a068c,0x1ea,DAT_004a06a8,cVar3);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004a06ac,DAT_004a06ac,cVar3);
      }
      *(undefined1 *)(*DAT_004a0518 + 0x59) = 0;
      *(undefined1 *)(*piVar1 + 0x15) = 0;
      if (cVar3 == '\0') {
        _SetRingLinkState(0,DAT_004a06b0);
      }
      else {
        *DAT_004a1168 = cVar3;
        uVar2 = DAT_004a116c;
        fw_event_loop_remove_delayed(DAT_004a116c);
        fw_event_loop_push_delayed(uVar2,cVar3,4000);
      }
    }
  }
  return;
}

