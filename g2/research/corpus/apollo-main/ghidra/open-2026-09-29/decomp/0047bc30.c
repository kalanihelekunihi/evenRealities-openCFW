
void FUN_0047bc30(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined1 *puVar8;
  int iVar9;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047c548,DAT_0047c544,DAT_0047c540,0x7d3,DAT_0047c53c);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_0047c54c,DAT_0047c54c);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047c548,DAT_0047c544,DAT_0047c540,0x7d4,DAT_0047c550,10);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0047c554,DAT_0047c554,10);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047c548,DAT_0047c544,DAT_0047c540,0x7d5,DAT_0047c55c,*DAT_0047c558);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0047c560,DAT_0047c560,*DAT_0047c558);
  }
  iVar1 = DAT_0047c158;
  iVar9 = 0;
  uVar3 = 0xffffffff;
  uVar4 = 0;
  iVar5 = 0;
  iVar6 = 0;
  FUN_00475014(0,1);
  for (iVar7 = 0; iVar7 < 10; iVar7 = iVar7 + 1) {
    puVar8 = (undefined1 *)(iVar1 + iVar7 * 0x100);
    if ((puVar8[0x30] == '\0') || (puVar8[0x2f] == '\0')) {
      if (puVar8[0x2f] == '\0') {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0047c548,DAT_0047c544,DAT_0047c540,0x7f7,DAT_0047c564,iVar7,
                       *(undefined4 *)(puVar8 + 0xc4));
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_0047c8a8,DAT_0047c8a8,iVar7,
                              *(undefined4 *)(puVar8 + 0xc4));
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0047c548,DAT_0047c544,DAT_0047c540,0x7f4,DAT_0047c8ac,iVar7,
                       *(undefined4 *)(puVar8 + 0xc4));
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_0047c8b0,DAT_0047c8b0,iVar7,
                              *(undefined4 *)(puVar8 + 0xc4));
        }
      }
    }
    else {
      iVar9 = iVar9 + 1;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0047c548,DAT_0047c544,DAT_0047c540,0x7e4,DAT_0047c8b4,iVar7,
                     *(undefined4 *)(puVar8 + 0xc4),puVar8[0x2e]);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10c00000,DAT_0047c8b8,DAT_0047c8b8,iVar7,
                            *(undefined4 *)(puVar8 + 0xc4),puVar8[0x2e]);
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0047c548,DAT_0047c544,DAT_0047c540,0x7e7,DAT_0047c8bc,puVar8[5],puVar8[4]
                     ,puVar8[3],puVar8[2],puVar8[1],*puVar8,puVar8[6]);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x11c00000,DAT_0047c8c0,DAT_0047c8c0,puVar8[5],puVar8[4],puVar8[3],
                            puVar8[2],puVar8[1],*puVar8,puVar8[6]);
      }
      if (*(uint *)(puVar8 + 0xc4) < uVar3) {
        uVar3 = *(uint *)(puVar8 + 0xc4);
        iVar5 = iVar7;
      }
      if (uVar4 < *(uint *)(puVar8 + 0xc4)) {
        uVar4 = *(uint *)(puVar8 + 0xc4);
        iVar6 = iVar7;
      }
    }
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047c548,DAT_0047c544,DAT_0047c540,0x7fb,DAT_0047c8c4,iVar9,10);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10800000,DAT_0047c8c8,DAT_0047c8c8,iVar9,10);
  }
  if (0 < iVar9) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0047c548,DAT_0047c544,DAT_0047c540,0x7fd,DAT_0047ca98,iVar5,uVar3);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_0047cac0,DAT_0047cac0,iVar5,uVar3);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0047c548,DAT_0047c544,DAT_0047c540,0x7fe,DAT_0047cac4,iVar6,uVar4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_0047cac8,DAT_0047cac8,iVar6,uVar4);
    }
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047c548,DAT_0047c544,DAT_0047c540,0x800,DAT_0047cacc);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_0047cad0,DAT_0047cad0);
  }
  return;
}

