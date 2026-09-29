
byte * FUN_005964e2(ushort param_1)

{
  undefined4 *puVar1;
  int iVar2;
  byte *pbVar3;
  undefined *puVar4;
  ushort uVar5;
  
  puVar1 = DAT_00596998;
  if (*(char *)((int)DAT_00596998 + 10) == '\0') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00596a8c,DAT_00596a88,DAT_00596a84,0x105,DAT_00596a68);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__conversate_tag_Storage_not_init_00596a6c,
                          PTR_s__conversate_tag_Storage_not_init_00596a6c);
    }
    pbVar3 = (byte *)0x0;
  }
  else if (param_1 < *(ushort *)(DAT_00596998 + 2)) {
    pbVar3 = (byte *)*DAT_00596998;
    uVar5 = 0;
    while ((uVar5 < param_1 && (pbVar3 != (byte *)0x0))) {
      pbVar3 = *(byte **)(pbVar3 + 0x14);
      if ((pbVar3 == (byte *)*DAT_00596998) && (uVar5 + 1 < (uint)param_1)) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00596a8c,DAT_00596a88,DAT_00596a84,0x115,DAT_00596a98,uVar5 + 1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_00596a9c,DAT_00596a9c,uVar5 + 1);
        }
        return (byte *)0x0;
      }
      uVar5 = uVar5 + 1;
    }
    if (pbVar3 == (byte *)0x0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00596a8c,DAT_00596a88,DAT_00596a84,0x11b,DAT_00596aa0,param_1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00596aa4,DAT_00596aa4,param_1);
      }
      pbVar3 = (byte *)0x0;
    }
    else if ((*pbVar3 == 0) || (4 < *pbVar3)) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00596a8c,DAT_00596a88,DAT_00596a84,0x120,DAT_00596aa8,*pbVar3);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00596aac,DAT_00596aac,*pbVar3);
      }
      pbVar3 = (byte *)0x0;
    }
    else if ((*(int *)(pbVar3 + 4) == 0) ||
            (iVar2 = FUN_0044a43c(*(undefined4 *)(pbVar3 + 4)), iVar2 == 0)) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        puVar4 = PTR_DAT_00596a78;
        if (*(int *)(pbVar3 + 4) != 0) {
          puVar4 = *(undefined **)(pbVar3 + 4);
        }
        FUN_0043d574(1,DAT_00596a8c,DAT_00596a88,DAT_00596a84,0x125,DAT_00596ab0,puVar4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        puVar4 = PTR_DAT_00596a78;
        if (*(int *)(pbVar3 + 4) != 0) {
          puVar4 = *(undefined **)(pbVar3 + 4);
        }
        compress_log_output(0x4400000,DAT_00596ab4,DAT_00596ab4,puVar4);
      }
      pbVar3 = (byte *)0x0;
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00596a8c,DAT_00596a88,DAT_00596a84,0x10b,DAT_00596a90,param_1,
                   *(undefined2 *)(puVar1 + 2));
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_00596a94,DAT_00596a94,param_1,*(undefined2 *)(puVar1 + 2));
    }
    pbVar3 = (byte *)0x0;
  }
  return pbVar3;
}

