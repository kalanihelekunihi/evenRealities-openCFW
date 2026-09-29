
undefined4 FUN_004efffc(void)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  int iVar7;
  undefined *puVar8;
  undefined4 uVar9;
  int iVar10;
  undefined4 in_r3;
  uint uVar11;
  undefined1 auStack_98 [12];
  uint local_8c;
  uint local_88;
  uint local_84;
  uint local_80;
  undefined4 local_7c;
  undefined1 auStack_70 [12];
  uint local_64;
  uint local_60;
  uint local_5c;
  undefined1 auStack_48 [32];
  undefined4 uStack_28;
  
  iVar4 = DAT_004f0cb4;
  piVar1 = DAT_004f0cb0;
  if ((*DAT_004f0cac == 0) || (*DAT_004f0cb0 < 0)) {
    uVar2 = 0;
  }
  else {
    uStack_28 = in_r3;
    if (*(int *)(DAT_004f0cb4 + *DAT_004f0cb0 * 8 + 4) != 0) {
      FUN_0044d878(*(undefined4 *)(DAT_004f0cb4 + *DAT_004f0cb0 * 8 + 4));
    }
    osMutexAcquire(*DAT_004f0e00,0xffffffff);
    iVar3 = FUN_004effda();
    osMutexRelease(*DAT_004f0e00);
    if (iVar3 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004f0e0c,DAT_004f0e08,DAT_004f0e04,0xb5,DAT_004f0cb8);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004f0cbc,DAT_004f0cbc);
      }
      if (*(int *)(iVar4 + *piVar1 * 8 + 4) == 0) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004f0e0c,DAT_004f0e08,DAT_004f0e04,0xb9,DAT_004f0e10,*piVar1,
                       *piVar1 + 1);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_004f0e14,DAT_004f0e14,*piVar1,*piVar1 + 1);
        }
        uVar2 = 0xffffffff;
      }
      else {
        uVar5 = FUN_0043de82(*(undefined4 *)(iVar4 + *piVar1 * 8 + 4));
        FUN_0043f09a(uVar5,0x14,0x10);
        FUN_0043f506(uVar5,0x13b);
        FUN_0043f568(uVar5,0x100);
        uVar2 = FUN_0044104c(0);
        FUN_0044127e(uVar5,uVar2,0);
        FUN_0044129e(uVar5,0,0);
        FUN_0044131c(uVar5,0,0);
        FUN_0044133a(uVar5,0,0);
        FUN_00441378(uVar5,0,0);
        FUN_00441386(uVar5,0,0);
        FUN_004413b0(uVar5,0,0);
        FUN_00441394(uVar5,0,0);
        FUN_004413a2(uVar5,0,0);
        FUN_004effa8(uVar5,0,0);
        FUN_0044120e(uVar5,0,0);
        FUN_0044121c(uVar5,0,0);
        FUN_0044122a(uVar5,0,0);
        FUN_00441238(uVar5,0,0);
        FUN_0044146a(uVar5,0,0);
        uVar2 = FUN_0044104c(0);
        FUN_004412ec(uVar5,uVar2,0);
        uVar2 = FUN_0044104c(0xffffff);
        FUN_0044140e(uVar5,uVar2,0);
        FUN_0044142e(uVar5,0xff,0);
        uVar2 = FUN_0043de82(uVar5);
        FUN_0043f4c0(uVar2,0x3fffffff,0x3fffffff);
        FUN_0044129e(uVar2,0,0);
        FUN_0044131c(uVar2,0,0);
        FUN_004effa8(uVar2,0,0);
        FUN_0048ba78(uVar2,0);
        FUN_0048ba92(uVar2,2,2,2);
        FUN_00441254(uVar2,8,0);
        FUN_0043f6b8(uVar2,2,0,100);
        uVar6 = FUN_00498668(uVar2);
        FUN_00498680(uVar6,DAT_004f0f08);
        FUN_0043f506(uVar6,0x18);
        FUN_0043f568(uVar6,0x18);
        FUN_0043ded4(uVar6,0x10000);
        FUN_0043dfa4(uVar6,0x10);
        iVar4 = FUN_00499416(uVar2);
        uVar2 = DAT_004f0f14;
        if (iVar4 == 0) {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(1,DAT_004f0e0c,DAT_004f0e08,DAT_004f0e04,0xea,DAT_004f0f0c);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_004f0f10,DAT_004f0f10);
          }
          uVar2 = 0xffffffff;
        }
        else {
          uVar6 = FUN_00460084(DAT_004f0f14);
          uVar2 = FUN_0045fffe(uVar2,uVar6);
          FUN_0049942e(iVar4,uVar2);
          piVar1 = DAT_004f0f18;
          FUN_0044143e(iVar4,*DAT_004f0f18,0);
          uVar2 = FUN_0044104c(0xffffff);
          FUN_0044140e(iVar4,uVar2,0);
          iVar4 = FUN_00499416(uVar5);
          uVar2 = DAT_004f1010;
          if (iVar4 == 0) {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              FUN_0043d574(1,DAT_004f0e0c,DAT_004f0e08,DAT_004f0e04,0xf3,DAT_004f0f0c);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0x4000000,DAT_004f0f10,DAT_004f0f10);
            }
            uVar2 = 0xffffffff;
          }
          else {
            uVar5 = FUN_00460084(DAT_004f1010);
            uVar2 = FUN_0045fffe(uVar2,uVar5);
            FUN_0049942e(iVar4,uVar2);
            FUN_0044143e(iVar4,*piVar1,0);
            uVar2 = FUN_0044104c(0xffffff);
            FUN_0044140e(iVar4,uVar2,0);
            FUN_0044145a(iVar4,2,0);
            FUN_0043f6b8(iVar4,2,0,0x82);
            uVar2 = 0;
          }
        }
      }
    }
    else if (*(int *)(iVar4 + *piVar1 * 8 + 4) == 0) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004f0e0c,DAT_004f0e08,DAT_004f0e04,0x101,DAT_004f1014,*piVar1,*piVar1 + 1
                    );
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4800000,DAT_004f1018,DAT_004f1018,*piVar1,*piVar1 + 1);
      }
      uVar2 = 0xffffffff;
    }
    else {
      uVar2 = FUN_0043de82(*(undefined4 *)(iVar4 + *piVar1 * 8 + 4));
      FUN_0043f09a(uVar2,0x14,0x10);
      FUN_0043f506(uVar2,0x13b);
      FUN_0043f568(uVar2,0x100);
      uVar5 = FUN_0044104c(0);
      FUN_0044127e(uVar2,uVar5,0);
      FUN_0044129e(uVar2,0,0);
      FUN_0044131c(uVar2,0,0);
      FUN_0044133a(uVar2,0,0);
      FUN_00441378(uVar2,0,0);
      FUN_00441386(uVar2,0,0);
      FUN_004413b0(uVar2,0,0);
      FUN_00441394(uVar2,0,0);
      FUN_004413a2(uVar2,0,0);
      FUN_004effa8(uVar2,0,0);
      FUN_0044120e(uVar2,0,0);
      FUN_0044121c(uVar2,0,0);
      FUN_0044122a(uVar2,0,0);
      FUN_00441238(uVar2,0,0);
      FUN_0044146a(uVar2,0,0);
      uVar5 = FUN_0044104c(0);
      FUN_004412ec(uVar2,uVar5,0);
      uVar5 = FUN_0044104c(0xffffff);
      FUN_0044140e(uVar2,uVar5,0);
      FUN_0044142e(uVar2,0xff,0);
      FUN_0043dfa4(uVar2,0x10);
      iVar4 = 0;
      osMutexAcquire(*DAT_004f0e00,0xffffffff);
      for (iVar3 = 0; iVar10 = DAT_004f0dfc, iVar3 < 5; iVar3 = iVar3 + 1) {
        if (*(char *)(DAT_004f0dfc + iVar3 * 0x1c98) == '\x01') {
          uVar5 = FUN_0043de82(uVar2);
          FUN_0043f506(uVar5,0x13b);
          FUN_0043f568(uVar5,0x3fffffff);
          FUN_0043f0e0(uVar5,0);
          FUN_0043f142(uVar5,iVar4);
          FUN_0044129e(uVar5,0,0);
          FUN_0044131c(uVar5,0,0);
          FUN_004effa8(uVar5,0,0);
          FUN_0044146a(uVar5,0,0);
          FUN_0043dfa4(uVar5,0x10);
          uVar6 = FUN_00498668(uVar5);
          FUN_00498680(uVar6,DAT_004f0f08);
          FUN_0043f506(uVar6,0x18);
          FUN_0043f568(uVar6,0x18);
          FUN_0043f0e0(uVar6,0);
          FUN_0043f142(uVar6,2);
          FUN_0043ded4(uVar6,0x10000);
          FUN_0043dfa4(uVar6,0x10);
          FUN_0043c0e4(auStack_48,0x20,0);
          iVar7 = iVar3 * 0x1c98 + iVar10;
          uVar6 = FUN_0047cc60(*(undefined4 *)(iVar7 + 0x1c90),*(undefined4 *)(iVar7 + 0x1c94),1000,
                               0);
          service_time_epoch_to_calendar(uVar6,auStack_98);
          service_time_current_calendar_get(auStack_70);
          if (local_8c < local_64) {
LAB_004f0660:
            iVar7 = FUN_00466500();
            if ((iVar7 == 0) || (iVar7 = FUN_00466500(), iVar7 == 1)) {
              FUN_0044b728(auStack_48,0x20,DAT_004f1274,local_88,local_84);
            }
            else {
              FUN_0044b728(auStack_48,0x20,DAT_004f1274,local_84,local_88);
            }
          }
          else {
            if (local_64 == local_8c) {
              if (local_88 < local_60) goto LAB_004f0660;
            }
            if (local_64 == local_8c) {
              if (local_60 == local_88) {
                if (local_84 < local_5c) goto LAB_004f0660;
              }
            }
            iVar7 = FUN_0046650c();
            if (iVar7 == 1) {
              uVar11 = local_80 % 0xc;
              if (uVar11 == 0) {
                uVar11 = 0xc;
              }
              if (local_80 < 0xc) {
                puVar8 = &DAT_004f0990;
              }
              else {
                puVar8 = &LAB_004f0994;
              }
              FUN_0044b728(auStack_48,0x20,DAT_004f1278,uVar11,local_7c,puVar8);
            }
            else {
              FUN_0044b728(auStack_48,0x20,DAT_004f127c,local_80,local_7c);
            }
          }
          uVar6 = FUN_00499416(uVar5);
          FUN_0043f506(uVar6,0x3fffffff);
          FUN_0043f568(uVar6,0x1c);
          FUN_0043f142(uVar6,0);
          FUN_0043f6b8(uVar6,3,0,0);
          FUN_0049942e(uVar6,auStack_48);
          uVar9 = FUN_0044104c(0xffffff);
          FUN_0044140e(uVar6,uVar9,0);
          piVar1 = DAT_004f0f18;
          FUN_0044143e(uVar6,*DAT_004f0f18,0);
          FUN_0043f66c(uVar6);
          iVar7 = FUN_0043fd9e(uVar6);
          iVar7 = 0x10f - iVar7;
          uVar6 = FUN_00499416(uVar5);
          FUN_0043f506(uVar6,iVar7);
          FUN_0043f568(uVar6,0x1c);
          FUN_0043f0e0(uVar6,0x20);
          FUN_0043f142(uVar6,0);
          FUN_00499678(uVar6,1);
          FUN_0049942e(uVar6,iVar3 * 0x1c98 + iVar10 + 1);
          uVar9 = FUN_0044104c(0xffffff);
          FUN_0044140e(uVar6,uVar9,0);
          FUN_0044143e(uVar6,*piVar1,0);
          if (iVar4 + 0x20 < 0xfa) {
            uVar6 = FUN_00499416(uVar5);
            FUN_0043f506(uVar6,0x13b);
            FUN_0043f0e0(uVar6,0);
            FUN_0043f142(uVar6,0x20);
            FUN_0049942e(uVar6,iVar3 * 0x1c98 + iVar10 + 0x81);
            uVar9 = FUN_0044104c(0xffffff);
            FUN_0044140e(uVar6,uVar9,0);
            FUN_0044143e(uVar6,*piVar1,0);
            FUN_0044144c(uVar6,0x1c - *(int *)(*piVar1 + 0xc),0);
            FUN_0043f568(uVar6,0x3fffffff);
            FUN_0043f66c(uVar6);
            iVar10 = FUN_0043fdda(uVar6);
            if (iVar10 < 0x55) {
              FUN_0043f568(uVar6,0x3fffffff);
              FUN_00499678(uVar6,0);
            }
            else {
              FUN_0043f568(uVar6,0x54);
              FUN_00499678(uVar6,1);
            }
          }
          FUN_0043f66c(uVar5);
          iVar10 = FUN_0043fdda(uVar5);
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            FUN_0043d574(3,DAT_004f0e0c,DAT_004f0e08,DAT_004f0e04,0x199,DAT_004f1384,iVar10);
          }
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1f < 0) {
LAB_004f08a4:
            compress_log_output(0xc400000,DAT_004f1388,DAT_004f1388,iVar10);
          }
          else {
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1d < 0) goto LAB_004f08a4;
          }
          iVar4 = iVar10 + iVar4 + 0x19;
          iVar10 = FUN_0043d0ce();
          if (iVar10 << 0x1e < 0) {
            FUN_0043d574(3,DAT_004f0e0c,DAT_004f0e08,DAT_004f0e04,0x19d,DAT_004f138c,iVar4);
          }
          iVar10 = FUN_0043d0ce();
          if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
            compress_log_output(0xc400000,DAT_004f1390,DAT_004f1390,iVar4);
          }
          if (0xfa < iVar4) break;
        }
      }
      uVar2 = osMutexRelease(*DAT_004f0e00);
    }
  }
  return uVar2;
}

