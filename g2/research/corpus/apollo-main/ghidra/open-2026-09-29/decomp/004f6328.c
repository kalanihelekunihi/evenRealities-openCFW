
undefined4 FUN_004f6328(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  undefined1 local_1250;
  undefined1 local_124f;
  undefined2 local_124e;
  undefined4 local_1248 [6];
  undefined2 local_1230 [102];
  undefined1 local_1164 [4412];
  undefined1 local_28;
  
  iVar1 = DAT_004f6d2c;
  if (*(short *)(DAT_004f6d2c + 0x280) == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004f6d3c,DAT_004f6d38,DAT_004f6d34,0x4c2,DAT_004f6d30);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004f6d40,DAT_004f6d40);
    }
  }
  else {
    uVar5 = (*(ushort *)(DAT_004f6d2c + 0x280) + 0x13) / 0x14;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004f6d3c,DAT_004f6d38,DAT_004f6d34,0x4d2,DAT_004f6d44,
                   *(undefined2 *)(iVar1 + 0x280),uVar5);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_004f6d48,DAT_004f6d48,*(undefined2 *)(iVar1 + 0x280),uVar5)
      ;
    }
    iVar2 = 0;
    for (iVar6 = 0; iVar6 < (int)uVar5; iVar6 = iVar6 + 1) {
      if ((int)((uint)*(ushort *)(iVar1 + 0x280) - iVar2) < 0x15) {
        iVar7 = (uint)*(ushort *)(iVar1 + 0x280) - iVar2;
      }
      else {
        iVar7 = 0x14;
      }
      FUN_0043c0e4(&local_1250,0x1230,0);
      local_1250 = 3;
      local_124f = (undefined1)*(undefined2 *)(iVar1 + 0x280);
      local_124e = (undefined2)iVar7;
      local_28 = 0;
      for (iVar4 = 0; iVar4 < iVar7; iVar4 = iVar4 + 1) {
        local_1248[iVar4 * 0x3a] = *(undefined4 *)(iVar1 + (iVar4 + iVar2) * 0x10);
        local_1248[iVar4 * 0x3a + 1] = 0;
        local_1248[iVar4 * 0x3a + 2] = 1;
        iVar8 = iVar1 + (iVar4 + iVar2) * 0x10;
        uVar3 = *(undefined4 *)(iVar8 + 0xc);
        local_1248[iVar4 * 0x3a + 4] = *(undefined4 *)(iVar8 + 8);
        local_1248[iVar4 * 0x3a + 5] = uVar3;
        local_1230[iVar4 * 0x74] = 0;
        local_1164[iVar4 * 0xe8] = 0;
      }
      iVar4 = APP_PbNotifyEncodeQuicklistMultItems(0,&local_1250);
      if (iVar4 != 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004f6d3c,DAT_004f6d38,DAT_004f6d34,0x4f1,DAT_004f6d68,iVar6,iVar4);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_004f6d70,DAT_004f6d70,iVar6,iVar4);
        }
        return 0xffffffff;
      }
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004f6d3c,DAT_004f6d38,DAT_004f6d34,0x4f5,DAT_004f6d4c,iVar6,iVar7);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_004f6d64,DAT_004f6d64,iVar6,iVar7);
      }
      iVar2 = iVar7 + iVar2;
    }
    FUN_0043c0e4(iVar1,0x288,0);
  }
  return 0;
}

