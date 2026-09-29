
undefined4 FUN_004eb7b8(int param_1)

{
  uint *puVar1;
  int *piVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  ushort uVar5;
  undefined2 uVar6;
  int iVar7;
  undefined4 uVar8;
  int iVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  uint uVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  uint local_3c;
  int local_38;
  int local_34;
  uint local_30;
  int local_2c;
  int local_28;
  
  if (param_1 == 0) {
    iVar7 = FUN_0043d0ce();
    if (iVar7 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004ebf1c,DAT_004ebdf8,DAT_004ec220,0x40f,DAT_004ec21c);
    }
    iVar7 = FUN_0043d0ce();
    if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ec224,DAT_004ec224);
    }
    uVar8 = 0xffffffff;
  }
  else {
    uVar5 = FUN_004e9fd6();
    if (uVar5 == 0) {
      iVar7 = FUN_004ebf20();
      if (iVar7 != 0) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          uVar8 = FUN_004ebf20();
          FUN_0043d574(4,DAT_004ebf1c,DAT_004ebdf8,DAT_004ec220,0x420,DAT_004ec234,uVar8);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          uVar8 = FUN_004ebf20();
          compress_log_output(0x10400000,DAT_004ec238,DAT_004ec238,uVar8);
        }
        *DAT_004ec230 = 0;
      }
    }
    else {
      uVar12 = (int)(uVar5 - 1) / 3;
      iVar7 = FUN_004ebf20();
      if ((int)(uVar12 & 0xffff) < iVar7) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          uVar8 = FUN_004ebf20();
          local_3c = uVar12 & 0xffff;
          FUN_0043d574(2,DAT_004ebf1c,DAT_004ebdf8,DAT_004ec220,0x41a,DAT_004ec228,uVar8,
                       uVar12 & 0xffff,uVar5);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          uVar8 = FUN_004ebf20();
          compress_log_output(0x9000000,DAT_004ec22c,DAT_004ec22c,uVar8,uVar12 & 0xffff,uVar5,
                              uVar12 & 0xffff);
        }
        *DAT_004ec230 = uVar12 & 0xffff;
      }
    }
    piVar2 = DAT_004ec23c;
    iVar7 = FUN_0043de82(param_1);
    *piVar2 = iVar7;
    if (*piVar2 == 0) {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004ebf1c,DAT_004ebdf8,DAT_004ec220,0x429,DAT_004ec240);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004ec244,DAT_004ec244);
      }
      uVar8 = 0xffffffff;
    }
    else {
      FUN_0043f09a(*piVar2,0x14,0x11);
      FUN_0043f4c0(*piVar2,0x21b,0xfe);
      FUN_0044e3ca(*piVar2,0xc);
      FUN_0044e368(*piVar2,0);
      FUN_0044129e(*piVar2,0,0);
      FUN_0044131c(*piVar2,0,0);
      FUN_004e9dd4(*piVar2,0,0);
      FUN_004ed12c(param_1);
      iVar7 = DAT_004ec248;
      FUN_004ea00c(DAT_004ec248,*piVar2,0,0);
      iVar13 = iVar7 + 0x60;
      FUN_004ea00c(iVar13,*piVar2,0x120,1);
      iVar14 = iVar7 + 0xc0;
      FUN_004ea00c(iVar14,*piVar2,0x240,2);
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004ebf1c,DAT_004ebdf8,DAT_004ec220,0x441,DAT_004ec24c,*DAT_004ec230);
      }
      iVar9 = FUN_0043d0ce();
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004ec250,DAT_004ec250,*DAT_004ec230);
      }
      FUN_004eac40();
      iVar9 = FUN_004e9fd6();
      if (iVar9 == 0) {
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004ebf1c,DAT_004ebdf8,DAT_004ec220,0x465,DAT_004ec264);
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004ec268,DAT_004ec268);
        }
        for (iVar9 = 0; uVar8 = DAT_004ec26c, iVar9 < 3; iVar9 = iVar9 + 1) {
          if (*(int *)(iVar7 + iVar9 * 0x60) != 0) {
            FUN_0043ded4(*(undefined4 *)(iVar7 + iVar9 * 0x60),1);
          }
        }
        local_34 = 8;
        uVar10 = FUN_00460084(DAT_004ec26c);
        uVar10 = FUN_0045fffe(uVar8,uVar10);
        uVar8 = DAT_004ec270;
        uVar11 = FUN_00460084(DAT_004ec270);
        uVar8 = FUN_0045fffe(uVar8,uVar11);
        puVar3 = DAT_004ec274;
        FUN_00489546(&local_3c,uVar10,*DAT_004ec274,0,0,0x1fffffff,0);
        local_30 = local_3c;
        iVar7 = local_38;
        if (local_38 < 0x19) {
          iVar7 = 0x18;
        }
        FUN_00489546(&local_2c,uVar8,*puVar3,0,0,0x21b,0);
        puVar4 = DAT_004ec278;
        if (0x21b < local_2c) {
          local_2c = 0x21b;
        }
        iVar15 = (0xfe - (local_28 + iVar7 + 4)) / 2;
        iVar14 = iVar7 + iVar15 + 4;
        iVar9 = (int)(0x21b - (local_30 + local_34 + 0x18)) / 2;
        iVar13 = local_34 + iVar9 + 0x18;
        uVar11 = FUN_00498668(*piVar2);
        *puVar4 = uVar11;
        FUN_0043f4c0(*puVar4,0x18,0x18);
        FUN_0043f09a(*puVar4,iVar9,(iVar7 + -0x18) / 2 + iVar15);
        FUN_00498680(*puVar4,DAT_004ec27c);
        puVar4 = DAT_004ec280;
        uVar11 = FUN_00499416(*piVar2);
        *puVar4 = uVar11;
        FUN_0043f4c0(*puVar4,0x3fffffff,0x3fffffff);
        FUN_0043f09a(*puVar4,iVar13,(iVar7 - local_38) / 2 + iVar15);
        FUN_0044145a(*puVar4,1,0);
        FUN_0044143e(*puVar4,*puVar3,0);
        uVar11 = FUN_0044104c(0xffffff);
        FUN_0044140e(*puVar4,uVar11,0);
        FUN_0049942e(*puVar4,uVar10);
        puVar4 = DAT_004ec284;
        uVar10 = FUN_00499416(*piVar2);
        *puVar4 = uVar10;
        FUN_0043f4c0(*puVar4,local_2c,0x3fffffff);
        FUN_0043f09a(*puVar4,(0x21b - local_2c) / 2,iVar14);
        FUN_0044145a(*puVar4,2,0);
        FUN_0044143e(*puVar4,*puVar3,0);
        uVar10 = FUN_0044104c(0xffffff);
        FUN_0044140e(*puVar4,uVar10,0);
        FUN_0049942e(*puVar4,uVar8);
      }
      else {
        FUN_004ea800(iVar7,0);
        iVar9 = FUN_004e9fd6();
        if (3 < iVar9) {
          FUN_004ea800(iVar13,1);
        }
        iVar9 = FUN_004e9fd6();
        if (6 < iVar9) {
          FUN_004ea800(iVar14,2);
        }
        FUN_004ed058(iVar7,0);
        FUN_004ed058(iVar13,1);
        FUN_004ed058(iVar14,2);
        puVar1 = DAT_004ec230;
        if (0 < (int)*DAT_004ec230) {
          iVar9 = *DAT_004ec230 * 0x120;
          FUN_0044ea04(*piVar2,iVar9,0);
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004ebf1c,DAT_004ebdf8,DAT_004ec220,0x45d,DAT_004ec254,iVar9,*puVar1);
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            compress_log_output(0x10800000,DAT_004ec258,DAT_004ec258,iVar9,*puVar1);
          }
        }
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004ebf1c,DAT_004ebdf8,DAT_004ec220,0x460,DAT_004ec25c);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004ec260,DAT_004ec260);
        }
      }
      FUN_004ed52e();
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        uVar6 = FUN_004e9fd6();
        FUN_0043d574(3,DAT_004ebf1c,DAT_004ebdf8,DAT_004ec220,0x4b8,DAT_004ec288,uVar6);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        uVar6 = FUN_004e9fd6();
        compress_log_output(0xc400000,DAT_004ec28c,DAT_004ec28c,uVar6);
      }
      uVar8 = 0;
    }
  }
  return uVar8;
}

