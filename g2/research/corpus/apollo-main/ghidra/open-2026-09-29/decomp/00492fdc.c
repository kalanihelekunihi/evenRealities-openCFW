
undefined4 FUN_00492fdc(uint param_1,char *param_2,int param_3,undefined4 param_4)

{
  char cVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  int *piVar5;
  int iVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  char *local_a4 [32];
  
  iVar6 = FUN_0043d0ce();
  if (iVar6 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00493514,DAT_00493510,DAT_00493564,0x9b,DAT_00493560,param_1);
  }
  iVar6 = FUN_0043d0ce();
  if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00493568,DAT_00493568,param_1);
  }
  piVar5 = DAT_00493580;
  if (param_1 == 2) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00493514,DAT_00493510,DAT_00493564,0x9e,DAT_0049356c,2);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00493570,DAT_00493570,2);
    }
    uVar8 = *(undefined4 *)(param_2 + 1);
    param_2 = param_2 + 5;
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      local_a4[0] = param_2;
      FUN_0043d574(3,DAT_00493514,DAT_00493510,DAT_00493564,0xa3,DAT_00493574,uVar8);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_00493578,DAT_00493578,uVar8,param_2);
    }
    puVar4 = DAT_0049357c;
    *DAT_0049357c = 0;
    puVar2 = DAT_00493500;
    *DAT_00493500 = 0;
    *DAT_00493528 = 0;
    *DAT_00493504 = 0;
    piVar5 = DAT_00493580;
    *DAT_00493580 = 900;
    puVar3 = DAT_0049351c;
    uVar7 = FUN_0043de82(param_4);
    *puVar3 = uVar7;
    uVar7 = FUN_004515d2(100);
    FUN_0043f506(*puVar3,uVar7);
    uVar7 = FUN_004515d2(100);
    FUN_0043f568(*puVar3,uVar7);
    FUN_0043f6ac(*puVar3,9);
    FUN_0043dfa4(*puVar3,0x10);
    FUN_0044129e(*puVar3,0,0);
    FUN_0044131c(*puVar3,0,0);
    FUN_0044133a(*puVar3,0,0);
    FUN_00441386(*puVar3,0,0);
    FUN_0044146a(*puVar3,0,0);
    FUN_00492cb4(*puVar3,0,0);
    FUN_0048ba78(*puVar3,1);
    FUN_0048ba92(*puVar3,2,2,2);
    uVar7 = FUN_0044104c(0xffffff);
    FUN_0044140e(*puVar3,uVar7,0);
    FUN_0044142e(*puVar3,0xff,0);
    iVar6 = UX_GetSystemBLEStatus();
    if (iVar6 == 0) {
      uVar8 = FUN_00499416(*puVar3);
      *puVar4 = uVar8;
      FUN_0043f506(*puVar4,0x3fffffff);
      FUN_0043f568(*puVar4,0x3fffffff);
      uVar8 = DAT_00493584;
      uVar7 = FUN_00460084(DAT_00493584);
      uVar8 = FUN_0045fffe(uVar8,uVar7);
      FUN_0049942e(*puVar4,uVar8);
      FUN_0044143e(*puVar4,*DAT_00493588,0);
      FUN_0044145a(*puVar4,2,0);
      *piVar5 = 300;
    }
    else {
      uVar7 = FUN_00499416(*puVar3);
      *puVar4 = uVar7;
      FUN_0043f506(*puVar4,0x23a);
      FUN_0043f568(*puVar4,0x3fffffff);
      FUN_00499678(*puVar4,0);
      FUN_0044143e(*puVar4,*DAT_00493588,0);
      FUN_0044145a(*puVar4,2,0);
      FUN_0043c0e4(local_a4,0x80,0);
      uVar7 = DAT_0049358c;
      uVar9 = FUN_00460084(DAT_0049358c);
      uVar7 = FUN_0045fffe(uVar7,uVar9);
      FUN_0044b728(local_a4,0x80,uVar7,param_2);
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00493514,DAT_00493510,DAT_00493564,0xce,DAT_00493590,local_a4);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_00493594,DAT_00493594,local_a4);
      }
      FUN_0049942e(*puVar4,local_a4);
      *puVar2 = uVar8;
      FUN_004d9e88(uVar8);
      *piVar5 = 900;
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00493514,DAT_00493510,DAT_00493564,0xd5,DAT_00493598,*puVar2);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_0049359c,DAT_0049359c,*puVar2);
    }
    *(undefined4 *)(DAT_004935a0 + 4) = *puVar3;
    return 0;
  }
  if (1 < param_1) {
    if (param_1 == 4) {
      if (*DAT_00493504 != 0) {
        return 0;
      }
      *DAT_00493580 = *DAT_00493580 + -1;
      if (0 < *piVar5) {
        return 0;
      }
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00493514,DAT_00493510,DAT_00493564,0xf0,DAT_004935bc);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004935c0,DAT_004935c0);
      }
      iVar6 = FUN_0045a568();
      if (iVar6 != 1) {
        return 0;
      }
      FUN_00464c36(0xffe,0,0,0);
      return 0;
    }
    if (param_1 < 4) {
      if (param_3 == 0) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(2,DAT_00493514,DAT_00493510,DAT_00493564,0xdb,DAT_004935a4);
        }
        iVar6 = FUN_0043d0ce();
        if ((-1 < iVar6 << 0x1f) && (iVar6 = FUN_0043d0ce(), -1 < iVar6 << 0x1d)) {
          return 0;
        }
        compress_log_output(0x8000000,DAT_004935a8,DAT_004935a8);
        return 0;
      }
      cVar1 = *param_2;
      if (cVar1 == '\x01') {
        cVar1 = param_2[1];
        param_2 = param_2 + 2;
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          local_a4[0] = param_2;
          FUN_0043d574(3,DAT_00493514,DAT_00493510,DAT_00493564,0xe2,DAT_004935ac,cVar1);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0xc800000,DAT_004935b0,DAT_004935b0,cVar1,param_2);
        }
        FUN_0049942e(*DAT_0049357c,param_2);
        FUN_0043f66c(*DAT_0049351c);
        *DAT_00493580 = 300;
        return 0;
      }
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(2,DAT_00493514,DAT_00493510,DAT_00493564,0xe7,DAT_004935b4,cVar1);
      }
      iVar6 = FUN_0043d0ce();
      if ((-1 < iVar6 << 0x1f) && (iVar6 = FUN_0043d0ce(), -1 < iVar6 << 0x1d)) {
        return 0;
      }
      compress_log_output(0x8400000,DAT_004935b8,DAT_004935b8,cVar1);
      return 0;
    }
    if (param_1 == 5) {
      *DAT_0049357c = 0;
      *DAT_00493528 = 0;
      *DAT_00493504 = 0;
      *DAT_00493580 = 0;
      *DAT_00493500 = 0;
      return 0;
    }
  }
  iVar6 = FUN_0043d0ce();
  if (iVar6 << 0x1e < 0) {
    FUN_0043d574(2,DAT_00493514,DAT_00493510,DAT_00493564,0x101,DAT_004935c4,param_1);
  }
  iVar6 = FUN_0043d0ce();
  if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
    compress_log_output(0x8400000,DAT_004935c8,DAT_004935c8,param_1);
  }
  return 0;
}

