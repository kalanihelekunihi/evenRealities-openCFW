
/* WARNING: Heritage AFTER dead removal. Example location: s1 : 0x004ec90e */
/* WARNING: Restarted to delay deadcode elimination for space: register */

undefined4 FUN_004ec2dc(uint param_1)

{
  undefined4 *puVar1;
  uint *puVar2;
  int *piVar3;
  undefined4 *puVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  int iVar9;
  int iVar10;
  uint uVar11;
  int iVar12;
  int iVar13;
  uint local_fc;
  int local_f8;
  int local_f4;
  uint local_f0;
  int local_ec;
  int local_e8;
  undefined1 auStack_e4 [32];
  undefined1 auStack_c4 [32];
  undefined1 auStack_a4 [32];
  undefined1 auStack_84 [32];
  undefined1 auStack_64 [32];
  undefined1 auStack_44 [32];
  
  puVar1 = DAT_004ecdac;
  *DAT_004ecdac = 0;
  puVar2 = DAT_004ece48;
  *DAT_004ece48 = param_1;
  piVar3 = DAT_004ecfc4;
  if (*puVar2 < 6) {
    if (*(int *)(DAT_004ece4c + *puVar2 * 8 + 4) == 0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004ecd50,DAT_004ed04c,DAT_004ed048,0x53f,DAT_004ecfbc,*puVar2);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_004ecfc0,DAT_004ecfc0,*puVar2);
      }
      uVar6 = 0xffffffff;
    }
    else {
      iVar5 = FUN_0043de82(*(undefined4 *)(DAT_004ece4c + *puVar2 * 8 + 4));
      *piVar3 = iVar5;
      if (*piVar3 == 0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004ecd50,DAT_004ed04c,DAT_004ed048,0x547,DAT_004ed050);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004ed054,DAT_004ed054);
        }
        uVar6 = 0xffffffff;
      }
      else {
        FUN_0043f09a(*piVar3,0x14,0x11);
        FUN_0043f4c0(*piVar3,0x13b,0xfe);
        FUN_0044129e(*piVar3,0,0);
        FUN_0044131c(*piVar3,0,0);
        FUN_004e9dd4(*piVar3,0,0);
        FUN_0044e368(*piVar3,0);
        iVar5 = FUN_004e9fd6();
        if (iVar5 == 0) {
          iVar5 = FUN_004ebf20();
          if (iVar5 != 0) {
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              uVar6 = FUN_004ebf20();
              FUN_0043d574(4,DAT_004ecd50,DAT_004ed04c,DAT_004ed048,0x563,DAT_004ed0fc,uVar6);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              uVar6 = FUN_004ebf20();
              compress_log_output(0x10400000,DAT_004ed100,DAT_004ed100,uVar6);
            }
            *DAT_004ed0f8 = 0;
          }
        }
        else {
          iVar5 = FUN_004e9fd6();
          uVar11 = (iVar5 + -1) / 3;
          iVar5 = FUN_004ebf20();
          if ((int)(uVar11 & 0xffff) < iVar5) {
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              uVar6 = FUN_004ebf20();
              local_fc = uVar11 & 0xffff;
              FUN_0043d574(2,DAT_004ecd50,DAT_004ed04c,DAT_004ed048,0x55d,DAT_004ed0e8,uVar6,
                           uVar11 & 0xffff,*DAT_004ecd4c);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              uVar6 = FUN_004ebf20();
              compress_log_output(0x9000000,DAT_004ed0f4,DAT_004ed0f4,uVar6,uVar11 & 0xffff,
                                  *DAT_004ecd4c,uVar11 & 0xffff);
            }
            *DAT_004ed0f8 = uVar11 & 0xffff;
          }
        }
        *puVar1 = 1;
        iVar5 = FUN_004e9fd6();
        uVar6 = DAT_004ed104;
        if (iVar5 == 0) {
          local_f4 = 8;
          uVar7 = FUN_00460084(DAT_004ed104);
          uVar7 = FUN_0045fffe(uVar6,uVar7);
          uVar6 = DAT_004ed108;
          uVar8 = FUN_00460084(DAT_004ed108);
          uVar6 = FUN_0045fffe(uVar6,uVar8);
          puVar1 = DAT_004ed10c;
          FUN_00489546(&local_fc,uVar7,*DAT_004ed10c,0,0,0x1fffffff,0);
          local_f0 = local_fc;
          iVar5 = local_f8;
          if (local_f8 < 0x19) {
            iVar5 = 0x18;
          }
          FUN_00489546(&local_ec,uVar6,*puVar1,0,0,0x13b,0);
          puVar4 = DAT_004ed110;
          if (0x13b < local_ec) {
            local_ec = 0x13b;
          }
          iVar13 = (0xfe - (local_e8 + iVar5 + 4)) / 2;
          iVar12 = iVar5 + iVar13 + 4;
          iVar9 = (int)(0x13b - (local_f0 + local_f4 + 0x18)) / 2;
          iVar10 = local_f4 + iVar9 + 0x18;
          uVar8 = FUN_00498668(*piVar3);
          *puVar4 = uVar8;
          FUN_0043f4c0(*puVar4,0x18,0x18);
          FUN_0043f09a(*puVar4,iVar9,(iVar5 + -0x18) / 2 + iVar13);
          FUN_00498680(*puVar4,DAT_004ed114);
          puVar4 = DAT_004ed118;
          uVar8 = FUN_00499416(*piVar3);
          *puVar4 = uVar8;
          FUN_0043f4c0(*puVar4,0x3fffffff,0x3fffffff);
          FUN_0043f09a(*puVar4,iVar10,(iVar5 - local_f8) / 2 + iVar13);
          FUN_0044145a(*puVar4,1,0);
          FUN_0044143e(*puVar4,*puVar1,0);
          uVar8 = FUN_0044104c(0xffffff);
          FUN_0044140e(*puVar4,uVar8,0);
          FUN_0049942e(*puVar4,uVar7);
          puVar4 = DAT_004ed11c;
          uVar7 = FUN_00499416(*piVar3);
          *puVar4 = uVar7;
          FUN_0043f4c0(*puVar4,local_ec,0x3fffffff);
          FUN_0043f09a(*puVar4,(0x13b - local_ec) / 2,iVar12);
          FUN_0044145a(*puVar4,2,0);
          FUN_0044143e(*puVar4,*puVar1,0);
          uVar7 = FUN_0044104c(0xffffff);
          FUN_0044140e(*puVar4,uVar7,0);
          FUN_0049942e(*puVar4,uVar6);
          uVar6 = 0;
        }
        else {
          iVar5 = FUN_004ebf20();
          iVar10 = iVar5 * 3 + 1;
          iVar12 = iVar5 * 3 + 2;
          iVar9 = FUN_004e9fd6();
          if (iVar5 * 3 < iVar9) {
            iVar9 = iVar5 * 0xc78 + DAT_004ed36c;
            uVar6 = FUN_00498668(*piVar3);
            FUN_0043f09a(uVar6,0,3);
            FUN_0043ded4(uVar6,0x10000);
            FUN_0043dfa4(uVar6,0x10);
            if (*(int *)(iVar9 + 0x134) == 1) {
              FUN_00498680(uVar6,DAT_004ed370);
            }
            else if (*(int *)(iVar9 + 0x134) == 2) {
              FUN_00498680(uVar6,DAT_004ed374);
            }
            else {
              FUN_00498680(uVar6,DAT_004ed378);
            }
            uVar6 = FUN_00499416(*piVar3);
            FUN_0043f4c0(uVar6,0x9c,0x1e);
            FUN_0043f09a(uVar6,0x20,0);
            puVar1 = DAT_004ed10c;
            FUN_0044143e(uVar6,*DAT_004ed10c,0);
            uVar7 = FUN_0044104c(0xffffff);
            FUN_0044140e(uVar6,uVar7,0);
            FUN_00499678(uVar6,1);
            FUN_0049942e(uVar6,iVar9);
            uVar6 = FUN_00499416(*piVar3);
            FUN_0043f4c0(uVar6,0x7e,0x1e);
            FUN_0043f09a(uVar6,0xbd,0);
            FUN_0044145a(uVar6,3,0);
            FUN_0044143e(uVar6,*puVar1,0);
            uVar7 = FUN_0044104c(0xffffff);
            FUN_0044140e(uVar6,uVar7,0);
            FUN_004ecee8(SUB84((double)*(float *)(iVar9 + 0x10c),0),auStack_44,0x20);
            FUN_0049942e(uVar6,auStack_44);
            uVar6 = FUN_00499416(*piVar3);
            FUN_0043f4c0(uVar6,0xc2,0x1c);
            FUN_0043f09a(uVar6,0,0x22);
            FUN_0044143e(uVar6,*puVar1,0);
            uVar7 = FUN_0044104c(0xffffff);
            FUN_0044140e(uVar6,uVar7,0);
            FUN_00499678(uVar6,1);
            FUN_0049942e(uVar6,iVar9 + 0x80);
            uVar6 = FUN_00499416(*piVar3);
            FUN_0043f4c0(uVar6,0x50,0x1c);
            FUN_0043f09a(uVar6,0xeb,0x22);
            FUN_0044145a(uVar6,3,0);
            FUN_0044143e(uVar6,*puVar1,0);
            uVar7 = FUN_0044104c(0xffffff);
            FUN_0044140e(uVar6,uVar7,0);
            FUN_004ecf3c(SUB84((double)*(float *)(iVar9 + 0x10c),0),
                         (int)((ulonglong)(double)*(float *)(iVar9 + 0x10c) >> 0x20),
                         SUB84((double)*(float *)(iVar9 + 0x108),0),auStack_64,0x20);
            FUN_0049942e(uVar6,auStack_64);
          }
          iVar9 = FUN_004e9fd6();
          if (iVar10 < iVar9) {
            iVar9 = iVar10 * 0x428 + DAT_004ed36c;
            uVar6 = FUN_00498668(*piVar3);
            FUN_0043f09a(uVar6,0,99);
            FUN_0043ded4(uVar6,0x10000);
            FUN_0043dfa4(uVar6,0x10);
            if (*(int *)(iVar9 + 0x134) == 1) {
              FUN_00498680(uVar6,DAT_004ed370);
            }
            else if (*(int *)(iVar9 + 0x134) == 2) {
              FUN_00498680(uVar6,DAT_004ed374);
            }
            else {
              FUN_00498680(uVar6,DAT_004ed378);
            }
            uVar6 = FUN_00499416(*piVar3);
            FUN_0043f4c0(uVar6,0x9c,0x1e);
            FUN_0043f09a(uVar6,0x20,0x60);
            puVar1 = DAT_004ed10c;
            FUN_0044143e(uVar6,*DAT_004ed10c,0);
            uVar7 = FUN_0044104c(0xffffff);
            FUN_0044140e(uVar6,uVar7,0);
            FUN_00499678(uVar6,1);
            FUN_0049942e(uVar6,iVar9);
            uVar6 = FUN_00499416(*piVar3);
            FUN_0043f4c0(uVar6,0x7e,0x1e);
            FUN_0043f09a(uVar6,0xbd,0x60);
            FUN_0044145a(uVar6,3,0);
            FUN_0044143e(uVar6,*puVar1,0);
            uVar7 = FUN_0044104c(0xffffff);
            FUN_0044140e(uVar6,uVar7,0);
            FUN_004ecee8(SUB84((double)*(float *)(iVar9 + 0x10c),0),auStack_84,0x20);
            FUN_0049942e(uVar6,auStack_84);
            uVar6 = FUN_00499416(*piVar3);
            FUN_0043f4c0(uVar6,0xc2,0x1c);
            FUN_0043f09a(uVar6,0,0x82);
            FUN_0044143e(uVar6,*puVar1,0);
            uVar7 = FUN_0044104c(0xffffff);
            FUN_0044140e(uVar6,uVar7,0);
            FUN_00499678(uVar6,1);
            FUN_0049942e(uVar6,iVar9 + 0x80);
            uVar6 = FUN_00499416(*piVar3);
            FUN_0043f4c0(uVar6,0x50,0x1c);
            FUN_0043f09a(uVar6,0xeb,0x82);
            FUN_0044145a(uVar6,3,0);
            FUN_0044143e(uVar6,*puVar1,0);
            uVar7 = FUN_0044104c(0xffffff);
            FUN_0044140e(uVar6,uVar7,0);
            FUN_004ecf3c(SUB84((double)*(float *)(iVar9 + 0x10c),0),
                         (int)((ulonglong)(double)*(float *)(iVar9 + 0x10c) >> 0x20),
                         SUB84((double)*(float *)(iVar9 + 0x108),0),auStack_a4,0x20);
            FUN_0049942e(uVar6,auStack_a4);
          }
          iVar9 = FUN_004e9fd6();
          if (iVar12 < iVar9) {
            iVar9 = DAT_004ed36c + iVar12 * 0x428;
            uVar6 = FUN_00498668(*piVar3);
            FUN_0043f09a(uVar6,0,0xc3);
            FUN_0043ded4(uVar6,0x10000);
            FUN_0043dfa4(uVar6,0x10);
            if (*(int *)(iVar9 + 0x134) == 1) {
              FUN_00498680(uVar6,DAT_004ed370);
            }
            else if (*(int *)(iVar9 + 0x134) == 2) {
              FUN_00498680(uVar6,DAT_004ed374);
            }
            else {
              FUN_00498680(uVar6,DAT_004ed378);
            }
            uVar6 = FUN_00499416(*piVar3);
            FUN_0043f4c0(uVar6,0x9c,0x1e);
            FUN_0043f09a(uVar6,0x20,0xc0);
            puVar1 = DAT_004ed10c;
            FUN_0044143e(uVar6,*DAT_004ed10c,0);
            uVar7 = FUN_0044104c(0xffffff);
            FUN_0044140e(uVar6,uVar7,0);
            FUN_00499678(uVar6,1);
            FUN_0049942e(uVar6,iVar9);
            uVar6 = FUN_00499416(*piVar3);
            FUN_0043f4c0(uVar6,0x7e,0x1e);
            FUN_0043f09a(uVar6,0xbd,0xc0);
            FUN_0044145a(uVar6,3,0);
            FUN_0044143e(uVar6,*puVar1,0);
            uVar7 = FUN_0044104c(0xffffff);
            FUN_0044140e(uVar6,uVar7,0);
            FUN_004ecee8(SUB84((double)*(float *)(iVar9 + 0x10c),0),auStack_c4,0x20);
            FUN_0049942e(uVar6,auStack_c4);
            uVar6 = FUN_00499416(*piVar3);
            FUN_0043f4c0(uVar6,0xc2,0x1c);
            FUN_0043f09a(uVar6,0,0xe2);
            FUN_0044143e(uVar6,*puVar1,0);
            uVar7 = FUN_0044104c(0xffffff);
            FUN_0044140e(uVar6,uVar7,0);
            FUN_00499678(uVar6,1);
            FUN_0049942e(uVar6,iVar9 + 0x80);
            uVar6 = FUN_00499416(*piVar3);
            FUN_0043f4c0(uVar6,0x50,0x1c);
            FUN_0043f09a(uVar6,0xeb,0xe2);
            FUN_0044145a(uVar6,3,0);
            FUN_0044143e(uVar6,*puVar1,0);
            uVar7 = FUN_0044104c(0xffffff);
            FUN_0044140e(uVar6,uVar7,0);
            FUN_004ecf3c(SUB84((double)*(float *)(iVar9 + 0x10c),0),
                         (int)((ulonglong)(double)*(float *)(iVar9 + 0x10c) >> 0x20),
                         SUB84((double)*(float *)(iVar9 + 0x108),0),auStack_e4,0x20);
            FUN_0049942e(uVar6,auStack_e4);
          }
          iVar9 = FUN_004ecfc8(iVar5);
          uVar7 = FUN_0043de82(*piVar3);
          FUN_0043f4c0(uVar7,0x138,1);
          FUN_0043f09a(uVar7,0,0x4f);
          uVar6 = DAT_004ed6c0;
          uVar8 = FUN_0044104c(DAT_004ed6c0);
          FUN_0044127e(uVar7,uVar8,0);
          FUN_0044129e(uVar7,0xff,0);
          FUN_0044131c(uVar7,0,0);
          FUN_004e9dd4(uVar7,0,0);
          uVar8 = FUN_0043de82(*piVar3);
          FUN_0043f4c0(uVar8,0x138,1);
          FUN_0043f09a(uVar8,0,0xaf);
          uVar6 = FUN_0044104c(uVar6);
          FUN_0044127e(uVar8,uVar6,0);
          FUN_0044129e(uVar8,0xff,0);
          FUN_0044131c(uVar8,0,0);
          FUN_004e9dd4(uVar8,0,0);
          if (iVar9 < 2) {
            FUN_0043ded4(uVar7,1);
          }
          else {
            iVar10 = FUN_0043d0ce();
            if (iVar10 << 0x1e < 0) {
              FUN_0043d574(4,DAT_004ed6e4,DAT_004ed04c,DAT_004ed048,0x697,DAT_004ed6e0,iVar5,iVar9);
            }
            iVar10 = FUN_0043d0ce();
            if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
              compress_log_output(0x10800000,DAT_004ed6e8,DAT_004ed6e8,iVar5,iVar9);
            }
          }
          if (iVar9 < 3) {
            FUN_0043ded4(uVar8,1);
          }
          else {
            iVar10 = FUN_0043d0ce();
            if (iVar10 << 0x1e < 0) {
              FUN_0043d574(4,DAT_004ed6e4,DAT_004ed04c,DAT_004ed048,0x69e,DAT_004ed6ec,iVar5,iVar9);
            }
            iVar10 = FUN_0043d0ce();
            if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
              compress_log_output(0x10800000,DAT_004ed6f0,DAT_004ed6f0,iVar5,iVar9);
            }
          }
          iVar10 = FUN_0043d0ce();
          if (iVar10 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004ed6e4,DAT_004ed04c,DAT_004ed048,0x6a1,DAT_004ed6f4,iVar5,iVar9);
          }
          iVar10 = FUN_0043d0ce();
          if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
            compress_log_output(0x10800000,DAT_004ed6f8,DAT_004ed6f8,iVar5,iVar9);
          }
          uVar6 = 0;
        }
      }
    }
  }
  else {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004ecd50,DAT_004ed04c,DAT_004ed048,0x539,DAT_004ecfb0,*puVar2);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004ecfb8,DAT_004ecfb8,*puVar2);
    }
    uVar6 = 0xffffffff;
  }
  return uVar6;
}

