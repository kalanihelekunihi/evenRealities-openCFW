
undefined4 FUN_0058d668(undefined1 *param_1)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  undefined4 *puVar7;
  
  if (param_1 == (undefined1 *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0058d9c8,DAT_0058d9c4,DAT_0058d9e8,0x49,DAT_0058d9e4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0058d9ec,DAT_0058d9ec);
    }
    uVar3 = 2;
  }
  else {
    if (*(ushort *)(param_1 + 2) < 0x15) {
      uVar6 = (uint)*(ushort *)(param_1 + 2);
    }
    else {
      uVar6 = 0x14;
    }
    if (param_1[1] == '\0') {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_0058d9c8,DAT_0058d9c4,DAT_0058d9e8,0x50,DAT_0058d9f0);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_0058d9f4,DAT_0058d9f4);
      }
      FUN_0043c0e4(DAT_0058d9c0,0x1238,0);
    }
    else if (*(short *)(param_1 + 2) == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0058d9c8,DAT_0058d9c4,DAT_0058d9e8,0x56,DAT_0058da04);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0058da08,DAT_0058da08);
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0058d9c8,DAT_0058d9c4,DAT_0058d9e8,0x5b,DAT_0058da0c,
                     *(undefined4 *)(param_1 + 0xc));
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0058da10,DAT_0058da10,*(undefined4 *)(param_1 + 0xc));
      }
      if (*(int *)(param_1 + 0xc) == 0) {
        FUN_0043c0e4(DAT_0058d9c0,0x1238,0);
      }
      iVar2 = DAT_0058d9c0;
      if (0x14 < (uint)*(byte *)(DAT_0058d9c0 + 0x1221) + (uVar6 & 0xff)) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0058d9c8,DAT_0058d9c4,DAT_0058d9e8,0x61,DAT_0058da14);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_0058da18,DAT_0058da18);
        }
        return 4;
      }
      for (iVar4 = 0; iVar4 < (int)(uVar6 & 0xff); iVar4 = iVar4 + 1) {
        puVar7 = (undefined4 *)(param_1 + iVar4 * 0xe8 + 8);
        if (*(uint *)(param_1 + iVar4 * 0xe8 + 0xc) < 0x14) {
          cVar1 = FUN_0058da28(puVar7,iVar2 + (iVar4 + (uint)*(byte *)(iVar2 + 0x1221)) * 0xe8);
          if (cVar1 == '\0') {
            *(undefined1 *)(iVar2 + iVar4 * 0xe8 + 0xe4) = 1;
          }
          else {
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              FUN_0043d574(1,DAT_0058d9c8,DAT_0058d9c4,DAT_0058d9e8,0x72,DAT_0058da1c,*puVar7);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0x4400000,DAT_0058da20,DAT_0058da20,*puVar7);
            }
          }
        }
        else {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(2,DAT_0058d9c8,DAT_0058d9c4,DAT_0058d9e8,0x6b,DAT_0058da24,
                         *(undefined4 *)(param_1 + iVar4 * 0xe8 + 0xc),*puVar7);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x8800000,DAT_0058dacc,DAT_0058dacc,
                                *(undefined4 *)(param_1 + iVar4 * 0xe8 + 0xc),*puVar7);
          }
        }
      }
    }
    iVar2 = DAT_0058d9c0;
    *(undefined1 *)(DAT_0058d9c0 + 0x1220) = param_1[1];
    *(char *)(iVar2 + 0x1221) = (char)uVar6 + *(char *)(iVar2 + 0x1221);
    *(undefined1 *)(iVar2 + 0x1222) = *param_1;
    uVar3 = service_time_current_epoch_get();
    *(undefined4 *)(iVar2 + 0x1228) = uVar3;
    *(undefined4 *)(iVar2 + 0x122c) = 0;
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(3,DAT_0058d9c8,DAT_0058d9c4,DAT_0058d9e8,0x80,DAT_0058d9fc,
                   *(undefined2 *)(param_1 + 2),*(undefined1 *)(iVar2 + 0x1220),
                   *(undefined1 *)(iVar2 + 0x1221));
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0xcc00000,DAT_0058da00,DAT_0058da00,*(undefined2 *)(param_1 + 2),
                          *(undefined1 *)(iVar2 + 0x1220),*(undefined1 *)(iVar2 + 0x1221));
    }
    if (*(byte *)(iVar2 + 0x1221) < *(byte *)(iVar2 + 0x1220)) {
      uVar3 = 1;
    }
    else {
      uVar3 = 0;
    }
  }
  return uVar3;
}

