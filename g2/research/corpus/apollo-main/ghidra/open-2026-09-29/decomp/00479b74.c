
undefined4 FUN_00479b74(undefined1 *param_1)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  bool bVar5;
  undefined1 *puVar6;
  bool bVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  undefined1 *puVar12;
  int iVar13;
  char cVar14;
  
  iVar3 = DAT_0047a2dc;
  iVar2 = FUN_0043d0ce(0);
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047a2e4,DAT_0047a2e0,DAT_0047a704,0x1be,DAT_0047a6ac);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_0047a6b0);
  }
  FUN_00475014(0,1);
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047a2e4,DAT_0047a2e0,DAT_0047a704,0x1ce,DAT_0047a708,DAT_0047a2dc,0x100,0x40
                );
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10c00000,DAT_0047a70c,DAT_0047a70c,DAT_0047a2dc,0x100,0x40);
  }
  iVar2 = iVar3;
  for (uVar8 = 0; (int)uVar8 < 10; uVar8 = uVar8 + 1) {
    bVar5 = true;
    bVar7 = true;
    bVar1 = true;
    for (iVar13 = 0; iVar13 < 6; iVar13 = iVar13 + 1) {
      if (*(char *)(iVar2 + iVar13) != '\0') {
        bVar7 = false;
      }
      if (*(char *)(iVar2 + iVar13) != -1) {
        bVar1 = false;
      }
    }
    if ((bVar7) || (bVar1)) {
      bVar5 = false;
    }
    if ((bVar5) && (iVar13 = FUN_004d294a(param_1), iVar13 != 0)) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0047a2e4,DAT_0047a2e0,DAT_0047a704,0x1e8,DAT_0047a710,uVar8);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0047a714,DAT_0047a714,uVar8);
      }
      FUN_004799a8(param_1,uVar8 & 0xff);
      FUN_004789b0(param_1,uVar8 & 0xff);
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0047a2e4,DAT_0047a2e0,DAT_0047a704,0x1ed,DAT_0047a718,uVar8);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0047a858,DAT_0047a858,uVar8);
      }
      return 1;
    }
    iVar2 = iVar2 + 0x100;
  }
  iVar2 = iVar3;
  for (uVar8 = 0; (int)uVar8 < 10; uVar8 = uVar8 + 1) {
    bVar7 = false;
    bVar1 = true;
    bVar5 = true;
    for (iVar13 = 0; iVar13 < 6; iVar13 = iVar13 + 1) {
      if (*(char *)(iVar2 + iVar13) != '\0') {
        bVar1 = false;
      }
      if (*(char *)(iVar2 + iVar13) != -1) {
        bVar5 = false;
      }
    }
    if ((bVar1) || (bVar5)) {
      bVar7 = true;
    }
    if (bVar7) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0047a2e4,DAT_0047a2e0,DAT_0047a704,0x20e,DAT_0047a894,uVar8);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0047a898,DAT_0047a898,uVar8);
      }
      FUN_004799a8(param_1,uVar8 & 0xff);
      FUN_004789b0(param_1,uVar8 & 0xff);
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0047a2e4,DAT_0047a2e0,DAT_0047a704,0x213,DAT_0047a89c,uVar8);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0047a8a0,DAT_0047a8a0,uVar8);
      }
      return 1;
    }
    iVar2 = iVar2 + 0x100;
  }
  uVar8 = (uint)(byte)param_1[0xc3];
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uVar4 = DAT_0047a8a8;
    if ((char)uVar8 != '\0') {
      uVar4 = DAT_0047a8a4;
    }
    FUN_0043d574(2,DAT_0047a2e4,DAT_0047a2e0,DAT_0047a704,0x222,DAT_0047a8ac,uVar4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    uVar4 = DAT_0047a8a8;
    if ((char)uVar8 != '\0') {
      uVar4 = DAT_0047a8a4;
    }
    compress_log_output(0x8400000,DAT_0047a8b0,DAT_0047a8b0,uVar4);
  }
  uVar9 = 0xffffffff;
  bVar1 = false;
  uVar11 = 0;
  do {
    cVar14 = (char)uVar8;
    puVar12 = (undefined1 *)0x0;
    uVar10 = 0;
    if (9 < (int)uVar11) {
LAB_00479f54:
      if (!bVar1) {
        for (uVar8 = 0; (int)uVar8 < 10; uVar8 = uVar8 + 1) {
          puVar6 = (undefined1 *)(iVar3 + uVar8 * 0x100);
          if (((puVar6[0x30] == '\0') && (puVar6[0x2f] == '\x01')) &&
             (*(uint *)(puVar6 + 0xc4) < uVar9)) {
            uVar9 = *(uint *)(puVar6 + 0xc4);
            bVar1 = true;
            puVar12 = puVar6;
            uVar10 = uVar8;
          }
        }
        if (bVar1) {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0047a2e4,DAT_0047a2e0,DAT_0047a704,0x249,DAT_0047a8bc,uVar10,uVar9);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x10800000,DAT_0047a8c0,DAT_0047a8c0,uVar10,uVar9);
          }
        }
      }
      if (!bVar1) {
        for (uVar8 = 0; (int)uVar8 < 10; uVar8 = uVar8 + 1) {
          puVar6 = (undefined1 *)(iVar3 + uVar8 * 0x100);
          if (((puVar6[0x30] != '\0') && (puVar6[0x2f] != '\0')) &&
             ((puVar6[0xc3] == cVar14 && (*(uint *)(puVar6 + 0xc4) < uVar9)))) {
            uVar9 = *(uint *)(puVar6 + 0xc4);
            puVar12 = puVar6;
            uVar10 = uVar8;
          }
        }
        if (puVar12 == (undefined1 *)0x0) {
          for (uVar8 = 0; (int)uVar8 < 10; uVar8 = uVar8 + 1) {
            puVar6 = (undefined1 *)(iVar3 + uVar8 * 0x100);
            if (((puVar6[0x30] != '\0') && (puVar6[0x2f] != '\0')) &&
               (*(uint *)(puVar6 + 0xc4) < uVar9)) {
              uVar9 = *(uint *)(puVar6 + 0xc4);
              puVar12 = puVar6;
              uVar10 = uVar8;
            }
          }
        }
        if (puVar12 == (undefined1 *)0x0) {
          for (uVar8 = 0; (int)uVar8 < 10; uVar8 = uVar8 + 1) {
            puVar6 = (undefined1 *)(iVar3 + uVar8 * 0x100);
            if (((puVar6[0x30] == '\0') && (puVar6[0x2f] == '\x01')) &&
               (*(uint *)(puVar6 + 0xc4) < uVar9)) {
              uVar9 = *(uint *)(puVar6 + 0xc4);
              puVar12 = puVar6;
              uVar10 = uVar8;
            }
          }
        }
      }
      if (puVar12 == (undefined1 *)0x0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0047ae28,DAT_0047adcc,DAT_0047a704,0x29c,DAT_0047ae3c);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_0047ae40,DAT_0047ae40);
        }
        uVar4 = 0;
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0047a2e4,DAT_0047a2e0,DAT_0047a704,0x27c,DAT_0047ab50,uVar10,
                       *(undefined4 *)(puVar12 + 0xc4));
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_0047ab54,DAT_0047ab54,uVar10,
                              *(undefined4 *)(puVar12 + 0xc4));
        }
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0047a2e4,DAT_0047a2e0,DAT_0047a704,0x27f,DAT_0047ab58,puVar12[5],
                       puVar12[4],puVar12[3],puVar12[2],puVar12[1],*puVar12);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x11800000,DAT_0047ab5c,DAT_0047ab5c,puVar12[5],puVar12[4],puVar12[3],
                              puVar12[2],puVar12[1],*puVar12);
        }
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0047a2e4,DAT_0047a2e0,DAT_0047a704,0x282,DAT_0047ab60,uVar10);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_0047ab64,DAT_0047ab64,uVar10);
        }
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0047a2e4,DAT_0047a2e0,DAT_0047a704,0x284,DAT_0047ab68,uVar10 << 6,
                       uVar10 << 8);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_0047acec,DAT_0047acec,uVar10 << 6,uVar10 << 8);
        }
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0047a2e4,DAT_0047a2e0,DAT_0047a704,0x285,DAT_0047acf0,uVar10 << 6);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_0047acf4,DAT_0047acf4,uVar10 << 6);
        }
        FUN_004799a8(param_1,uVar10 & 0xff);
        FUN_00475014(0,1);
        puVar12 = (undefined1 *)(iVar3 + uVar10 * 0x100);
        iVar3 = FUN_004d294a(puVar12,param_1);
        if (iVar3 == 0) {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(1,DAT_0047ae28,DAT_0047adcc,DAT_0047a704,0x291,DAT_0047adc8,uVar10);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x4400000,DAT_0047add0,DAT_0047add0,uVar10);
          }
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(1,DAT_0047ae28,DAT_0047adcc,DAT_0047a704,0x294,DAT_0047ae2c,param_1[5],
                         param_1[4],param_1[3],param_1[2],param_1[1],*param_1);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x5800000,DAT_0047ae30,DAT_0047ae30,param_1[5],param_1[4],param_1[3]
                                ,param_1[2],param_1[1],*param_1);
          }
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(1,DAT_0047ae28,DAT_0047adcc,DAT_0047a704,0x297,DAT_0047ae34,puVar12[5],
                         puVar12[4],puVar12[3],puVar12[2],puVar12[1],*puVar12);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x5800000,DAT_0047ae38,DAT_0047ae38,puVar12[5],puVar12[4],puVar12[3]
                                ,puVar12[2],puVar12[1],*puVar12);
          }
        }
        else {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0047a2e4,DAT_0047a2e0,DAT_0047a704,0x28f,DAT_0047ad6c,puVar12[5],
                         puVar12[4],puVar12[3],puVar12[2],puVar12[1],*puVar12,uVar10);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x11c00000,DAT_0047ad70,DAT_0047ad70,puVar12[5],puVar12[4],
                                puVar12[3],puVar12[2],puVar12[1],*puVar12,uVar10);
          }
        }
        uVar4 = 1;
      }
      return uVar4;
    }
    puVar12 = (undefined1 *)(iVar3 + uVar11 * 0x100);
    FUN_004789b0(puVar12,uVar11 & 0xff);
    cVar14 = (char)uVar8;
    if ((puVar12[0x30] == '\0') && (puVar12[0x2f] == '\0')) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0047a2e4,DAT_0047a2e0,DAT_0047a704,0x231,DAT_0047a8b4,uVar11);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0047a8b8,DAT_0047a8b8,uVar11);
      }
      bVar1 = true;
      uVar10 = uVar11;
      goto LAB_00479f54;
    }
    uVar11 = uVar11 + 1;
  } while( true );
}

