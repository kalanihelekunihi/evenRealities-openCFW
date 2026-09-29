
void FUN_004f1ab8(int param_1)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;
  int *piVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined *puVar8;
  undefined4 uVar9;
  int iVar10;
  int iVar11;
  uint uVar12;
  int iVar13;
  undefined1 auStack_94 [12];
  uint local_88;
  uint local_84;
  uint local_80;
  uint local_7c;
  undefined4 local_78;
  undefined1 auStack_6c [12];
  uint local_60;
  uint local_5c;
  uint local_58;
  undefined1 auStack_44 [32];
  
  piVar1 = DAT_004f1ef8;
  if (*DAT_004f1ef8 == 0) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004f23e0,DAT_004f23dc,DAT_004f252c,0x3cc,DAT_004f2528);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004f2530,DAT_004f2530);
    }
  }
  else {
    iVar5 = 0;
    for (iVar11 = 0; iVar10 = -1, iVar11 < 5; iVar11 = iVar11 + 1) {
      if (*(char *)(DAT_004f2534 + iVar11 * 0x1c98) == '\x01') {
        iVar10 = iVar11;
        if (iVar5 == param_1) break;
        iVar5 = iVar5 + 1;
      }
    }
    if (iVar10 < 0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004f23e0,DAT_004f23dc,DAT_004f252c,0x3dd,DAT_004f2538,param_1);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_004f253c,DAT_004f253c,param_1);
      }
    }
    else {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(3,DAT_004f23e0,DAT_004f23dc,DAT_004f252c,0x3e1,DAT_004f2540,iVar10,
                     DAT_004f2534 + iVar10 * 0x1c98 + 0x81);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0xc800000,DAT_004f2544,DAT_004f2544,iVar10,
                            DAT_004f2534 + iVar10 * 0x1c98 + 0x81);
      }
      piVar2 = DAT_004f2548;
      iVar5 = FUN_0043de82(*piVar1);
      *piVar2 = iVar5;
      if (*piVar2 == 0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004f23e0,DAT_004f23dc,DAT_004f252c,1000,DAT_004f254c);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004f2550,DAT_004f2550);
        }
      }
      else {
        FUN_0043f4c0(*piVar2,0x23c,0xfc);
        FUN_0043f09a(*piVar2,0,0x10);
        FUN_0044129e(*piVar2,0,0);
        FUN_0044131c(*piVar2,0,0);
        FUN_0044122a(*piVar2,0x14,0);
        FUN_00441238(*piVar2,8,0);
        FUN_0044120e(*piVar2,0,0);
        FUN_0044121c(*piVar2,0x10,0);
        FUN_0044146a(*piVar2,0,0);
        FUN_00441478(*piVar2,1,0);
        FUN_0043dfa4(*piVar2,0x10);
        piVar1 = DAT_004f27f8;
        iVar5 = FUN_0043de82(*piVar2);
        *piVar1 = iVar5;
        if (*piVar1 == 0) {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(1,DAT_004f23e0,DAT_004f23dc,DAT_004f252c,0x3ff,DAT_004f27fc);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_004f2800,DAT_004f2800);
          }
        }
        else {
          iVar13 = 0x21a;
          FUN_0043f506(*piVar1,0x21a);
          FUN_0043f568(*piVar1,0x3fffffff);
          FUN_0043f09a(*piVar1,0,0);
          FUN_0044129e(*piVar1,0,0);
          FUN_0044131c(*piVar1,0,0);
          FUN_0044122a(*piVar1,0,0);
          FUN_00441238(*piVar1,0,0);
          FUN_0044120e(*piVar1,2,0);
          FUN_0044121c(*piVar1,0,0);
          FUN_0044146a(*piVar1,0,0);
          FUN_0043dfa4(*piVar1,0x10);
          FUN_0048ba78(*piVar1,1);
          FUN_00441246(*piVar1,0x1c,0);
          uVar6 = FUN_0043de82(*piVar1);
          FUN_0043f506(uVar6,iVar13);
          FUN_0043f568(uVar6,0x3fffffff);
          FUN_0044129e(uVar6,0,0);
          FUN_0044131c(uVar6,0,0);
          FUN_004effa8(uVar6,0,0);
          FUN_0043dfa4(uVar6,0x10);
          uVar7 = FUN_00498668(uVar6);
          FUN_00498680(uVar7,DAT_004f28dc);
          FUN_0043f4c0(uVar7,0x18,0x18);
          FUN_0043f09a(uVar7,0,2);
          FUN_0043ded4(uVar7,0x10000);
          FUN_0043dfa4(uVar7,0x10);
          FUN_0043c0e4(auStack_44,0x20,0);
          iVar5 = DAT_004f2534;
          iVar11 = iVar10 * 0x1c98 + DAT_004f2534;
          uVar7 = FUN_0047cc60(*(undefined4 *)(iVar11 + 0x1c90),*(undefined4 *)(iVar11 + 0x1c94),
                               1000,0);
          service_time_epoch_to_calendar(uVar7,auStack_94);
          service_time_current_calendar_get(auStack_6c);
          if (((local_88 < local_60) || ((local_60 == local_88 && (local_84 < local_5c)))) ||
             ((local_60 == local_88 && ((local_5c == local_84 && (local_80 < local_58)))))) {
            iVar11 = FUN_00466500();
            if ((iVar11 == 0) || (iVar11 = FUN_00466500(), iVar11 == 1)) {
              FUN_0044b728(auStack_44,0x20,DAT_004f28e0,local_84,local_80);
            }
            else {
              FUN_0044b728(auStack_44,0x20,DAT_004f28e0,local_80,local_84);
            }
          }
          else {
            iVar11 = FUN_0046650c();
            if (iVar11 == 1) {
              uVar12 = local_7c % 0xc;
              if (uVar12 == 0) {
                uVar12 = 0xc;
              }
              if (local_7c < 0xc) {
                puVar8 = &DAT_004f225c;
              }
              else {
                puVar8 = &DAT_004f2260;
              }
              FUN_0044b728(auStack_44,0x20,DAT_004f28e4,uVar12,local_78,puVar8);
            }
            else {
              FUN_0044b728(auStack_44,0x20,DAT_004f28e8,local_7c,local_78);
            }
          }
          uVar7 = FUN_00499416(uVar6);
          FUN_0043f506(uVar7,0x3fffffff);
          FUN_0043f568(uVar7,0x1c);
          FUN_0043f6b8(uVar7,3,0,0);
          FUN_0049942e(uVar7,auStack_44);
          uVar9 = FUN_0044104c(0xffffff);
          FUN_0044140e(uVar7,uVar9,0);
          piVar3 = DAT_004f28ec;
          FUN_0044143e(uVar7,*DAT_004f28ec,0);
          FUN_0043f66c(uVar7);
          iVar11 = FUN_0043fd9e(uVar7);
          uVar6 = FUN_00499416(uVar6);
          FUN_0043f506(uVar6,(iVar13 + -0x2c) - iVar11);
          FUN_0043f568(uVar6,0x1c);
          FUN_0043f09a(uVar6,0x20,0);
          FUN_00499678(uVar6,1);
          FUN_0049942e(uVar6,iVar10 * 0x1c98 + iVar5 + 1);
          uVar7 = FUN_0044104c(0xffffff);
          FUN_0044140e(uVar6,uVar7,0);
          FUN_0044143e(uVar6,*piVar3,0);
          uVar6 = FUN_00499416(*piVar1);
          FUN_0043f506(uVar6,400);
          FUN_0043f568(uVar6,0x3fffffff);
          FUN_00499678(uVar6,0);
          FUN_0049942e(uVar6,iVar10 * 0x1c98 + iVar5 + 0x81);
          uVar7 = FUN_0044104c(0xffffff);
          FUN_0044140e(uVar6,uVar7,0);
          FUN_0044143e(uVar6,*piVar3,0);
          FUN_0044144c(uVar6,0x1c - *(int *)(*piVar3 + 0xc),0);
          iVar11 = FUN_0044a43c(iVar10 * 0x1c98 + iVar5 + 0x101);
          if (iVar11 != 0) {
            uVar6 = FUN_00499416(*piVar1);
            FUN_0043f506(uVar6,iVar13);
            FUN_0043f568(uVar6,0x3fffffff);
            FUN_00499678(uVar6,0);
            FUN_0049942e(uVar6,iVar5 + iVar10 * 0x1c98 + 0x101);
            uVar7 = FUN_0044104c(0xffffff);
            FUN_0044140e(uVar6,uVar7,0);
            FUN_0044143e(uVar6,*piVar3,0);
            FUN_0044144c(uVar6,0x1c - *(int *)(*piVar3 + 0xc),0);
          }
          FUN_0043f66c(*piVar1);
          piVar3 = DAT_004f2b94;
          iVar5 = FUN_0043fdda(*piVar1);
          *piVar3 = iVar5;
          piVar1 = DAT_004f2b98;
          *DAT_004f2b98 = 0xec;
          *DAT_004f2b9c = 0;
          *DAT_004f2ba0 = 0;
          *DAT_004f2ba4 = 0;
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(3,DAT_004f23e0,DAT_004f23dc,DAT_004f252c,0x47c,DAT_004f2ba8,*piVar3,*piVar1
                        );
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0xc800000,DAT_004f2bac,DAT_004f2bac,*piVar3,*piVar1);
          }
          piVar4 = DAT_004f2bb0;
          if (*piVar1 < *piVar3) {
            iVar5 = *piVar1;
            iVar11 = (*piVar1 * iVar5) / *piVar3;
            if (iVar11 < 0x10) {
              iVar11 = 0x10;
            }
            iVar10 = FUN_0043de82(*piVar2);
            *piVar4 = iVar10;
            if (*piVar4 != 0) {
              FUN_0043f4c0(*piVar4,2,iVar11);
              FUN_0043f09a(*piVar4,0x220,0);
              uVar6 = FUN_0044104c(DAT_004f2bb4);
              FUN_0044127e(*piVar4,uVar6,0);
              FUN_0044129e(*piVar4,0x7f,0);
              FUN_0044131c(*piVar4,0,0);
              FUN_0044146a(*piVar4,1,0);
              FUN_004effa8(*piVar4,0,0);
              FUN_0043dfa4(*piVar4,0x10);
              iVar10 = FUN_0043d0ce();
              if (iVar10 << 0x1e < 0) {
                FUN_0043d574(3,DAT_004f23e0,DAT_004f23dc,DAT_004f252c,0x497,DAT_004f2bb8,iVar11,
                             iVar5,0x14);
              }
              iVar10 = FUN_0043d0ce();
              if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
                compress_log_output(0xcc00000,DAT_004f2e94,DAT_004f2e94,iVar11,iVar5,0x14);
              }
            }
          }
        }
      }
    }
  }
  return;
}

