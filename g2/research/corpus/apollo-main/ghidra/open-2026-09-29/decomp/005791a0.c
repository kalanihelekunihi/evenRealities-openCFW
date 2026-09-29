
undefined4 semantic_CodecDownloadBootStage2(void)

{
  undefined1 *puVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 in_r3;
  uint uVar5;
  int iVar6;
  uint local_28;
  int local_24;
  undefined4 uStack_20;
  
  iVar3 = DAT_00579658;
  local_24 = 0;
  local_28 = 0;
  uVar5 = 0;
  iVar6 = *DAT_0057965c + *(int *)(DAT_00579658 + 8) + 0x20;
  uStack_20 = in_r3;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00579c7c,DAT_00579c78,DAT_00579c74,0x211,DAT_00579c70);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_00579c80,DAT_00579c80);
  }
  local_28 = *(uint *)(iVar3 + 0x10);
  local_24 = *(int *)(iVar3 + 0x14);
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00579c7c,DAT_00579c78,DAT_00579c74,0x215,DAT_00579c84,local_28,local_24);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10800000,DAT_00579c88,DAT_00579c88,local_28,local_24);
  }
  puVar1 = DAT_005799e4;
  if ((local_24 == 0) || (local_28 == 0)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00579c7c,DAT_00579c78,DAT_00579c74,0x218,DAT_00579c8c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00579c90,DAT_00579c90);
    }
    uVar4 = 0xffffffff;
  }
  else {
    *DAT_005799e4 = 0x53;
    FUN_0058fb38(puVar1,1);
    FUN_0058fb38(&local_24,4);
    FUN_0058fb38(&local_28,4);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00579c7c,DAT_00579c78,DAT_00579c74,0x221,DAT_00579c94);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00579c98,DAT_00579c98);
    }
    iVar3 = semantic_CodecWaitForUartToken(DAT_00579c9c,10000);
    if (iVar3 < 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(2,DAT_00579c7c,DAT_00579c78,DAT_00579c74,0x223,DAT_00579ca0);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_00579ca4,DAT_00579ca4);
      }
      uVar4 = 0xffffffff;
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00579c7c,DAT_00579c78,DAT_00579c74,0x226,DAT_00579ca8);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00579cac,DAT_00579cac);
      }
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00579c7c,DAT_00579c78,DAT_00579c74,0x228,DAT_00579cb0);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00579cb4,DAT_00579cb4);
      }
      for (; uVar5 < local_28; uVar5 = uVar5 + 0x100) {
        FUN_00439be4(puVar1,iVar6,0x100);
        iVar6 = iVar6 + 0x100;
        FUN_0058fb38(puVar1,0x100);
      }
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00579c7c,DAT_00579c78,DAT_00579c74,0x232,DAT_00579cb8,uVar5);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_00579f50,DAT_00579f50,uVar5);
      }
      iVar3 = semantic_CodecWaitForUartToken(&DAT_00579640,10000);
      if (iVar3 < 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(2,DAT_00579c7c,DAT_00579c78,DAT_00579c74,0x234,DAT_00579f54);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_00579f58,DAT_00579f58);
        }
        uVar4 = 0xffffffff;
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00579c7c,DAT_00579c78,DAT_00579c74,0x237,DAT_00579f5c);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_00579f60,DAT_00579f60);
        }
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00579c7c,DAT_00579c78,DAT_00579c74,0x239,DAT_00579f64);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_00579f68,DAT_00579f68);
        }
        iVar3 = semantic_CodecWaitForUartToken(DAT_00579f6c,10000);
        if (iVar3 == 0) {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,DAT_00579c7c,DAT_00579c78,DAT_00579c74,0x23e,DAT_00579f78);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_00579f7c,DAT_00579f7c);
          }
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,DAT_00579c7c,DAT_00579c78,DAT_00579c74,0x240,DAT_00579f80);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_00579f84,DAT_00579f84);
          }
          uVar4 = 0;
        }
        else {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(2,DAT_00579c7c,DAT_00579c78,DAT_00579c74,0x23b,DAT_00579f70);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x8000000,DAT_00579f74,DAT_00579f74);
          }
          uVar4 = 0xffffffff;
        }
      }
    }
  }
  return uVar4;
}

