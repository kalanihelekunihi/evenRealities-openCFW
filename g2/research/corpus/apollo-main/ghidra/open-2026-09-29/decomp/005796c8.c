
undefined4 semantic_CodecFlashImage(void)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int local_28;
  undefined4 local_24;
  
  FUN_0043c0e4(&local_28,4,0);
  piVar1 = DAT_00579f88;
  iVar8 = *DAT_00579f88;
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00579c7c,DAT_00579c78,DAT_00579f90,0x251,DAT_00579f8c);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_00579f94,DAT_00579f94);
  }
  piVar2 = DAT_00579f98;
  local_28 = *DAT_00579f98;
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00579c7c,DAT_00579c78,DAT_00579f90,0x254,DAT_00579f9c,local_28);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00579fa0,DAT_00579fa0,local_28);
  }
  uVar4 = DAT_005799e4;
  if (local_28 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00579c7c,DAT_00579c78,DAT_00579f90,599,DAT_00579fa4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00579fa8,DAT_00579fa8);
    }
    uVar4 = 0xffffffff;
  }
  else {
    FUN_0043c0e4(DAT_005799e4,0x2000,0);
    uVar5 = FUN_004b4728(uVar4,DAT_00579fac,0,local_28,0x2000);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00579c7c,DAT_00579c78,DAT_00579f90,0x25d,DAT_00579fb0,uVar5,uVar4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_00579fb4,DAT_00579fb4,uVar5,uVar4);
    }
    FUN_0058fb38(uVar4,uVar5);
    local_24 = FUN_0058fcf0(0xffffffff,*piVar2,*piVar1);
    FUN_0058fb38(&local_24,4);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00579c7c,DAT_00579c78,DAT_00579f90,0x263,DAT_0057a360);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0057a364,DAT_0057a364);
    }
    uVar4 = DAT_0057a368;
    iVar3 = semantic_CodecWaitForUartToken(DAT_0057a368,DAT_0057a36c);
    if (iVar3 < 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(2,DAT_00579c7c,DAT_00579c78,DAT_00579f90,0x265,DAT_0057a370);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0057a374,DAT_0057a374);
      }
      uVar4 = 0xffffffff;
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00579c7c,DAT_00579c78,DAT_00579f90,0x268,DAT_0057a378);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_0057a37c,DAT_0057a37c);
      }
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00579c7c,DAT_00579c78,DAT_00579f90,0x26a,DAT_0057a380);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_0057a384,DAT_0057a384);
      }
      iVar9 = 0;
      iVar3 = local_28;
      while (0 < iVar3) {
        iVar7 = iVar3;
        if (0x2000 < iVar3) {
          iVar7 = 0x2000;
        }
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00579c7c,DAT_00579c78,DAT_00579f90,0x272,DAT_0057a388,iVar3,iVar7);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_0057a38c,DAT_0057a38c,iVar3,iVar7);
        }
        FUN_0058fb38(iVar8 + iVar9,iVar7);
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00579c7c,DAT_00579c78,DAT_00579f90,0x276,DAT_0057a390);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_0057a394,DAT_0057a394);
        }
        iVar6 = semantic_CodecWaitForUartToken(DAT_0057a398,10000);
        if (iVar6 < 0) {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(2,DAT_00579c7c,DAT_00579c78,DAT_00579f90,0x279,DAT_0057a39c);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x8000000,DAT_0057a3a0,DAT_0057a3a0);
          }
          return 0xffffffff;
        }
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00579c7c,DAT_00579c78,DAT_00579f90,0x27c,DAT_0057a3a4);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_0057a3a8,DAT_0057a3a8);
        }
        iVar3 = iVar3 - iVar7;
        iVar9 = iVar7 + iVar9;
        if (0 < iVar3) {
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            FUN_0043d574(4,DAT_00579c7c,DAT_00579c78,DAT_00579f90,0x284,DAT_0057a360);
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_0057a364,DAT_0057a364);
          }
          iVar7 = semantic_CodecWaitForUartToken(uVar4,10000);
          if (iVar7 < 0) {
            iVar3 = FUN_0043d0ce();
            if (iVar3 << 0x1e < 0) {
              FUN_0043d574(2,DAT_00579c7c,DAT_00579c78,DAT_00579f90,0x286,DAT_0057a370);
            }
            iVar3 = FUN_0043d0ce();
            if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
              compress_log_output(0x8000000,DAT_0057a374,DAT_0057a374);
            }
            return 0xffffffff;
          }
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            FUN_0043d574(4,DAT_00579c7c,DAT_00579c78,DAT_00579f90,0x289,DAT_0057a378);
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_0057a37c);
          }
        }
      }
      iVar3 = semantic_CodecWaitForUartToken(DAT_0057a3ac,3000);
      if ((iVar3 == 0) && (iVar3 = semantic_CodecWaitForUartToken(DAT_0057a3b0,2000), iVar3 == 0)) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(3,DAT_00579c7c,DAT_00579c78,DAT_00579f90,0x291,DAT_0057a3bc);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_0057a3c0,DAT_0057a3c0);
        }
        uVar4 = 0;
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(2,DAT_00579c7c,DAT_00579c78,DAT_00579f90,0x28e,DAT_0057a3b4);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_0057a3b8,DAT_0057a3b8);
        }
        uVar4 = 0xffffffff;
      }
    }
  }
  return uVar4;
}

