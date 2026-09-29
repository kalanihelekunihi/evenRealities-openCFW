
undefined4 FUN_004f4678(void)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;
  int *piVar4;
  int *piVar5;
  undefined4 *puVar6;
  int iVar7;
  undefined4 uVar8;
  int iVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  undefined4 uVar12;
  int unaff_r4;
  int iVar13;
  
  piVar1 = DAT_004f4f78;
  if (unaff_r4 == 0) {
    iVar7 = FUN_0043d0ce();
    if (iVar7 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004f4f70,DAT_004f4f6c,DAT_004f4f68);
    }
    iVar7 = FUN_0043d0ce();
    if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004f4f74,DAT_004f4f74);
    }
    uVar8 = 0xffffffff;
  }
  else {
    if (*DAT_004f4f78 != 0) {
      ui_common_api_fn_00509c96(*DAT_004f4f78);
      *piVar1 = 0;
    }
    iVar7 = ui_common_api_fn_00509c1c();
    *piVar1 = iVar7;
    if (*piVar1 == 0) {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004f4f70,DAT_004f4f6c,DAT_004f4f68);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004f4f80);
      }
      uVar8 = 0xffffffff;
    }
    else {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004f4f70,DAT_004f4f6c,DAT_004f4f68);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004f4f88,DAT_004f4f88);
      }
      piVar1 = DAT_004f4f8c;
      *DAT_004f4f8c = 0;
      piVar2 = DAT_004f4f90;
      *DAT_004f4f90 = 0;
      piVar3 = DAT_004f4f94;
      *DAT_004f4f94 = 0;
      piVar4 = DAT_004f4f98;
      *DAT_004f4f98 = 0;
      piVar5 = DAT_004f4f9c;
      *DAT_004f4f9c = 0;
      *DAT_004f4ebc = 0;
      *DAT_004f4fa0 = 0;
      *DAT_004f4fa4 = 0;
      *DAT_004f4fa8 = 0;
      *DAT_004f4fac = 0;
      *DAT_004f4fb0 = 0;
      *DAT_004f4fb4 = 0;
      for (iVar7 = 0; iVar7 < 5; iVar7 = iVar7 + 1) {
        *(undefined4 *)(DAT_004f4fb8 + iVar7 * 4) = 0;
      }
      *DAT_004f4fbc = 0;
      *DAT_004f4fc0 = 0;
      *DAT_004f4fc4 = 0;
      *DAT_004f4fc8 = 0;
      *DAT_004f4fcc = 0;
      *DAT_004f4fd0 = 0;
      *DAT_004f4fd4 = 0;
      *DAT_004f4fd8 = 0;
      *DAT_004f4fdc = 0;
      puVar6 = DAT_004f4fe0;
      osMutexAcquire(*DAT_004f4fe0,0xffffffff);
      iVar7 = FUN_004effda();
      osMutexRelease(*puVar6);
      iVar13 = 0;
      if (iVar7 == 5) {
        iVar7 = FUN_0043de82();
        *piVar1 = iVar7;
        if (*piVar1 == 0) {
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            FUN_0043d574(1,DAT_004f4f70,DAT_004f4f6c,DAT_004f4f68);
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_004f4fe8,DAT_004f4fe8);
          }
          return 0xffffffff;
        }
        FUN_0043f4c0(*piVar1,0x240,0x120);
        FUN_0043f09a(*piVar1,0xffffffff,0xffffffff);
        uVar8 = FUN_0044104c(0);
        FUN_0044127e(*piVar1,uVar8,0);
        FUN_0044129e(*piVar1,0xff,0);
        FUN_0044131c(*piVar1,0,0);
        FUN_004effa8(*piVar1,0,0);
        FUN_0044146a(*piVar1,0,0);
        FUN_0043dfa4(*piVar1,0x10);
        iVar7 = FUN_0043de82(*piVar1);
        *piVar2 = iVar7;
        if (*piVar2 == 0) {
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            FUN_0043d574(1,DAT_004f4f70,DAT_004f4f6c,DAT_004f4f68);
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_004f4ff0,DAT_004f4ff0);
          }
          return 0xffffffff;
        }
        FUN_0043f4c0(*piVar2,0x240,0x120);
        FUN_0043f09a(*piVar2,0,0);
        FUN_0044129e(*piVar2,0,0);
        FUN_0044131c(*piVar2,0,0);
        uVar8 = FUN_0044104c(0);
        FUN_004412ec(*piVar2,uVar8,0);
        FUN_0044146a(*piVar2,6,0);
        FUN_0044122a(*piVar2,8,0);
        FUN_00441238(*piVar2,0xe,0);
        FUN_0044120e(*piVar2,0,0);
        FUN_0044121c(*piVar2,0x120,0);
        FUN_0044e3ca(*piVar2,0xc);
        FUN_0044e368(*piVar2,3);
        FUN_00441164(*piVar2,1,0x10000);
        uVar8 = FUN_0044104c(0xffffff);
        FUN_0044127e(*piVar2,uVar8,0x10000);
        FUN_0044129e(*piVar2,0x7f,0x10000);
        osMutexAcquire(*puVar6,0xffffffff);
        iVar7 = 0;
        while ((iVar7 < 5 && (*piVar4 < 5))) {
          if ((*(char *)(DAT_004f4ff4 + iVar7 * 0x1c98) == '\x01') &&
             (iVar9 = FUN_004f0998(*piVar2,DAT_004f4ff4 + iVar7 * 0x1c98,iVar13,*piVar4), iVar9 != 0
             )) {
            *(int *)(DAT_004f4fb8 + *piVar4 * 4) = iVar9;
            FUN_0043f66c(iVar9);
            iVar9 = FUN_0043fdda(iVar9);
            iVar13 = iVar9 + iVar13 + 10;
            *piVar4 = *piVar4 + 1;
          }
          iVar7 = iVar7 + 1;
        }
        osMutexRelease(*puVar6);
        iVar7 = FUN_004f0cc0(*piVar2,iVar13);
        *piVar5 = iVar7;
        if (*piVar5 == 0) {
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            FUN_0043d574(1,DAT_004f4f70,DAT_004f4f6c,DAT_004f4f68);
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_004f5004,DAT_004f5004);
          }
        }
        else {
          FUN_0043f66c(*piVar5);
          FUN_0043fdda(*piVar5);
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            FUN_0043fce0(*piVar5);
            FUN_0043d574(3,DAT_004f4f70,DAT_004f4f6c,DAT_004f4f68);
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            uVar8 = FUN_0043fce0(*piVar5);
            compress_log_output(0xcc00000,DAT_004f4ffc,DAT_004f4ffc,uVar8);
          }
        }
        *piVar3 = 0;
        if (((0 < *piVar3) && (*piVar3 < *piVar4)) && (*(int *)(DAT_004f4fb8 + *piVar3 * 4) != 0)) {
          uVar8 = FUN_0043fce0();
          FUN_0044ea04(*piVar2,uVar8,0);
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004f4f70,DAT_004f4f6c,DAT_004f4f68);
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            compress_log_output(0x10800000,DAT_004f500c,DAT_004f500c,*piVar3);
          }
        }
        FUN_004f0e18(*piVar3);
      }
      else {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004f4f70,DAT_004f4f6c,DAT_004f4f68);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004f5014,DAT_004f5014);
        }
        iVar7 = FUN_0043de82();
        *piVar1 = iVar7;
        if (*piVar1 == 0) {
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            FUN_0043d574(1,DAT_004f4f70,DAT_004f4f6c,DAT_004f4f68);
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_004f501c,DAT_004f501c);
          }
          return 0xffffffff;
        }
        FUN_0043f4c0(*piVar1,0x240,0x120);
        FUN_0043f09a(*piVar1,0xffffffff,0xffffffff);
        uVar8 = FUN_0044104c(0);
        FUN_0044127e(*piVar1,uVar8,0);
        FUN_0044129e(*piVar1,0,0);
        FUN_0044131c(*piVar1,0,0);
        FUN_004effa8(*piVar1,0,0);
        FUN_0044146a(*piVar1,0,0);
        FUN_0043dfa4(*piVar1,0x10);
        uVar10 = FUN_0043de82(*piVar1);
        FUN_0043f4c0(uVar10,0x3fffffff,0x3fffffff);
        FUN_0044129e(uVar10,0,0);
        FUN_0044131c(uVar10,0,0);
        FUN_004effa8(uVar10,0,0);
        FUN_0048ba78(uVar10,1);
        FUN_0048ba92(uVar10,2,2,2);
        FUN_00441246(uVar10,6,0);
        FUN_0043f6b8(uVar10,9,0,0);
        uVar8 = FUN_0043de82(uVar10);
        FUN_0043f4c0(uVar8,0x3fffffff,0x3fffffff);
        FUN_0044129e(uVar8,0,0);
        FUN_0044131c(uVar8,0,0);
        FUN_004effa8(uVar8,0,0);
        FUN_0048ba78(uVar8,0);
        FUN_0048ba92(uVar8,2,2,2);
        FUN_00441254(uVar8,8,0);
        uVar11 = FUN_00498668(uVar8);
        FUN_00498680(uVar11,DAT_004f5020);
        FUN_0043f506(uVar11,0x18);
        FUN_0043f568(uVar11,0x18);
        FUN_0043ded4(uVar11,0x10000);
        FUN_0043dfa4(uVar11,0x10);
        uVar11 = FUN_00499416(uVar8);
        uVar8 = DAT_004f5024;
        uVar12 = FUN_00460084(DAT_004f5024);
        uVar8 = FUN_0045fffe(uVar8,uVar12);
        FUN_0049942e(uVar11,uVar8);
        uVar8 = FUN_0044104c(0xffffff);
        FUN_0044140e(uVar11,uVar8,0);
        puVar6 = DAT_004f5028;
        FUN_0044143e(uVar11,*DAT_004f5028,0);
        uVar10 = FUN_00499416(uVar10);
        uVar8 = DAT_004f502c;
        uVar11 = FUN_00460084(DAT_004f502c);
        uVar8 = FUN_0045fffe(uVar8,uVar11);
        FUN_0049942e(uVar10,uVar8);
        uVar8 = FUN_0044104c(0xffffff);
        FUN_0044140e(uVar10,uVar8,0);
        FUN_0044143e(uVar10,*puVar6,0);
        FUN_0044145a(uVar10,2,0);
      }
      *DAT_004f5030 = 1;
      FUN_004fe1b4(0,0);
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(3,DAT_004f4f70,DAT_004f4f6c,DAT_004f4f68);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_004f5038,DAT_004f5038,*piVar4);
      }
      uVar8 = 0;
    }
  }
  return uVar8;
}

