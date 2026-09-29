
undefined4 FUN_00475fe8(void)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  undefined4 in_r3;
  int iVar4;
  undefined4 local_60 [4];
  undefined1 auStack_50 [52];
  undefined4 uStack_1c;
  
  uStack_1c = in_r3;
  FUN_00439c04(local_60,DAT_00476454,0x10);
  iVar4 = 0;
  do {
    uVar1 = DAT_00476474;
    if (3 < iVar4) {
      return 0;
    }
    iVar2 = FUN_004cfc66(DAT_00476474,auStack_50,local_60[iVar4]);
    if (iVar2 == -2) {
      iVar2 = FUN_004cfc5c(uVar1,local_60[iVar4]);
      if (iVar2 == 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00476464,DAT_00476460,DAT_0047645c,0x51,DAT_00476458,local_60[iVar4]);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_00476468,DAT_00476468,local_60[iVar4]);
        }
      }
      else if (iVar2 == -0x11) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00476464,DAT_00476460,DAT_0047645c,0x53,DAT_00476478,local_60[iVar4]);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_0047647c,DAT_0047647c,local_60[iVar4]);
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(2,DAT_00476464,DAT_00476460,DAT_0047645c,0x55,DAT_00476480,local_60[iVar4],
                       iVar2);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8800000,DAT_00476484,DAT_00476484,local_60[iVar4],iVar2);
        }
      }
    }
    else {
      if (iVar2 != 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(2,DAT_00476464,DAT_00476460,DAT_0047645c,0x5c,DAT_00476488,local_60[iVar4],
                       iVar2);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8800000,DAT_0047648c,DAT_0047648c,local_60[iVar4],iVar2);
        }
        return 0xffffffff;
      }
      FUN_004cfcf8(uVar1,auStack_50);
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00476464,DAT_00476460,DAT_0047645c,0x5a,DAT_0047646c,local_60[iVar4]);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_00476470,DAT_00476470,local_60[iVar4]);
      }
    }
    iVar4 = iVar4 + 1;
  } while( true );
}

