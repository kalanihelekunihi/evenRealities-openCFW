
void FUN_004eef7c(void)

{
  undefined4 *puVar1;
  ushort *puVar2;
  int *piVar3;
  int *piVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  int iVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  int iVar11;
  int iVar12;
  
  if (*DAT_004efc9c == 0) {
    uVar6 = FUN_0043de82();
    FUN_0043f4c0(uVar6,0x21b,0x100);
    FUN_0043f09a(uVar6,0x14,0x10);
    FUN_0044e3ca(uVar6,0xc);
    FUN_0044e368(uVar6,3);
    FUN_004ed7d8(uVar6,0,0);
    FUN_0044131c(uVar6,0,0);
    FUN_0044129e(uVar6,0,0);
    uVar7 = FUN_0044104c(0xffffff);
    FUN_0044127e(uVar6,uVar7,0x10000);
    FUN_0044129e(uVar6,200,0x10000);
    uVar6 = FUN_0043de82(uVar6);
    FUN_0043f4c0(uVar6,0x3fffffff,0x3fffffff);
    FUN_0044129e(uVar6,0,0);
    FUN_0044131c(uVar6,0,0);
    FUN_004ed7d8(uVar6,0,0);
    FUN_0048ba78(uVar6,1);
    FUN_0048ba92(uVar6,2,2,2);
    FUN_00441246(uVar6,8,0);
    FUN_0043f6b8(uVar6,2,0,0x62);
    iVar8 = UX_GetSystemBLEStatus();
    if (iVar8 == 0) {
      uVar7 = FUN_0043de82(uVar6);
      FUN_0043f4c0(uVar7,0x3fffffff,0x3fffffff);
      FUN_0044129e(uVar7,0,0);
      FUN_0044131c(uVar7,0,0);
      FUN_004ed7d8(uVar7,0,0);
      FUN_0048ba78(uVar7,0);
      FUN_0048ba92(uVar7,2,2,2);
      FUN_00441254(uVar7,8,0);
      uVar9 = FUN_00498668(uVar7);
      FUN_00498680(uVar9,DAT_004efca0);
      FUN_0043f506(uVar9,0x18);
      FUN_0043f568(uVar9,0x18);
      FUN_0043ded4(uVar9,0x10000);
      FUN_0043dfa4(uVar9,0x10);
      uVar9 = FUN_00499416(uVar7);
      uVar7 = FUN_0044104c(0xffffff);
      FUN_0044140e(uVar9,uVar7,0);
      uVar7 = DAT_004efca4;
      uVar10 = FUN_00460084(DAT_004efca4);
      uVar7 = FUN_0045fffe(uVar7,uVar10);
      FUN_0049942e(uVar9,uVar7);
      puVar1 = DAT_004efca8;
      FUN_0044143e(uVar9,*DAT_004efca8,0);
      uVar7 = FUN_00499416(uVar6);
      uVar6 = FUN_0044104c(0xffffff);
      FUN_0044140e(uVar7,uVar6,0);
      uVar6 = DAT_004efcac;
      uVar9 = FUN_00460084(DAT_004efcac);
      uVar6 = FUN_0045fffe(uVar6,uVar9);
      FUN_0049942e(uVar7,uVar6);
      FUN_0044143e(uVar7,*puVar1,0);
      FUN_0044145a(uVar7,2,0);
    }
    else if (*DAT_004efcb0 == 1) {
      uVar6 = FUN_0043de82(uVar6);
      FUN_0043f4c0(uVar6,0x3fffffff,0x3fffffff);
      FUN_0044129e(uVar6,0,0);
      FUN_0044131c(uVar6,0,0);
      FUN_004ed7d8(uVar6,0,0);
      FUN_0048ba78(uVar6,0);
      FUN_0048ba92(uVar6,2,2,2);
      FUN_00441254(uVar6,8,0);
      uVar7 = FUN_00498668(uVar6);
      FUN_00498680(uVar7,DAT_004efca0);
      FUN_0043f506(uVar7,0x18);
      FUN_0043f568(uVar7,0x18);
      FUN_0043ded4(uVar7,0x10000);
      FUN_0043dfa4(uVar7,0x10);
      uVar7 = FUN_00499416(uVar6);
      uVar6 = DAT_004efcb4;
      uVar9 = FUN_00460084(DAT_004efcb4);
      uVar6 = FUN_0045fffe(uVar6,uVar9);
      FUN_0049942e(uVar7,uVar6);
      uVar6 = FUN_0044104c(0xffffff);
      FUN_0044140e(uVar7,uVar6,0);
      FUN_0044143e(uVar7,*DAT_004efca8,0);
    }
    else {
      uVar7 = FUN_0043de82(uVar6);
      FUN_0043f4c0(uVar7,0x3fffffff,0x3fffffff);
      FUN_0044129e(uVar7,0,0);
      FUN_0044131c(uVar7,0,0);
      FUN_004ed7d8(uVar7,0,0);
      FUN_0048ba78(uVar7,0);
      FUN_0048ba92(uVar7,2,2,2);
      FUN_00441254(uVar7,8,0);
      uVar9 = FUN_00498668(uVar7);
      FUN_00498680(uVar9,DAT_004efca0);
      FUN_0043f506(uVar9,0x18);
      FUN_0043f568(uVar9,0x18);
      FUN_0043ded4(uVar9,0x10000);
      FUN_0043dfa4(uVar9,0x10);
      uVar9 = FUN_00499416(uVar7);
      uVar7 = FUN_0044104c(0xffffff);
      FUN_0044140e(uVar9,uVar7,0);
      uVar7 = DAT_004efeac;
      uVar10 = FUN_00460084(DAT_004efeac);
      uVar7 = FUN_0045fffe(uVar7,uVar10);
      FUN_0049942e(uVar9,uVar7);
      puVar1 = DAT_004efca8;
      FUN_0044143e(uVar9,*DAT_004efca8,0);
      uVar7 = FUN_00499416(uVar6);
      uVar6 = FUN_0044104c(0xffffff);
      FUN_0044140e(uVar7,uVar6,0);
      uVar6 = DAT_004efee8;
      uVar9 = FUN_00460084(DAT_004efee8);
      uVar6 = FUN_0045fffe(uVar6,uVar9);
      FUN_0049942e(uVar7,uVar6);
      FUN_0044143e(uVar7,*puVar1,0);
      FUN_0044145a(uVar7,2,0);
    }
    *DAT_004efeec = 0;
    *DAT_004efa50 = 0;
    *DAT_004efef0 = 0;
    *DAT_004efef4 = 0;
    *DAT_004efa6c = 0;
    *DAT_004efa70 = 0;
  }
  else {
    uVar6 = FUN_0043de82();
    *DAT_004efeec = uVar6;
    FUN_0043f4c0(*DAT_004efeec,0x240,0x100);
    FUN_0043f09a(*DAT_004efeec,0,0x10);
    FUN_004ed7d8(*DAT_004efeec,0,0);
    FUN_0044131c(*DAT_004efeec,0,0);
    FUN_0044129e(*DAT_004efeec,0,0);
    FUN_0044146a(*DAT_004efeec,0,0);
    FUN_00441478(*DAT_004efeec,1,0);
    FUN_0043dfa4(*DAT_004efeec,0x10);
    puVar1 = DAT_004efa50;
    uVar6 = FUN_0043de82(*DAT_004efeec);
    *puVar1 = uVar6;
    FUN_0043f506(*puVar1,0x240);
    FUN_0043f09a(*puVar1,0,0);
    FUN_004ed7d8(*puVar1,0,0);
    FUN_0044131c(*puVar1,0,0);
    FUN_0044129e(*puVar1,0,0);
    FUN_0044146a(*puVar1,0,0);
    FUN_0043dfa4(*puVar1,0x10);
    *DAT_004efa6c = 0;
    *DAT_004efa70 = 0;
    iVar12 = 0;
    for (iVar8 = 0; iVar5 = DAT_004efefc, puVar2 = DAT_004efc9c, iVar8 < (int)(uint)*DAT_004efc9c;
        iVar8 = iVar8 + 1) {
      uVar6 = FUN_00498668(*puVar1);
      *(undefined4 *)(iVar5 + iVar8 * 0x18) = uVar6;
      FUN_00498680(*(undefined4 *)(iVar5 + iVar8 * 0x18),DAT_004efca0);
      FUN_0043f506(*(undefined4 *)(iVar5 + iVar8 * 0x18),0x18);
      FUN_0043f568(*(undefined4 *)(iVar5 + iVar8 * 0x18),0x18);
      FUN_0043f0e0(*(undefined4 *)(iVar5 + iVar8 * 0x18),0x14);
      FUN_0043f142(*(undefined4 *)(iVar5 + iVar8 * 0x18),iVar12 + 2);
      FUN_0043ded4(*(undefined4 *)(iVar5 + iVar8 * 0x18),0x10000);
      FUN_0043dfa4(*(undefined4 *)(iVar5 + iVar8 * 0x18),0x10);
      uVar6 = FUN_00499416(*puVar1);
      *(undefined4 *)(iVar8 * 0x18 + iVar5 + 4) = uVar6;
      FUN_0043f506(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 4),0x1fb);
      FUN_0043f568(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 4),0x1c);
      FUN_0043f0e0(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 4),0x34);
      FUN_0043f142(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 4),iVar12);
      FUN_00499678(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 4),1);
      FUN_0049942e(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 4),puVar2 + iVar8 * 0x108 + 2);
      uVar6 = FUN_0044104c(0xffffff);
      FUN_0044140e(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 4),uVar6,0);
      FUN_0044143e(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 4),*DAT_004efca8,0);
      osMutexAcquire(*DAT_004eff00,0xffffffff);
      iVar11 = FUN_0044a43c(puVar2 + iVar8 * 0x108 + 0x5a);
      osMutexRelease(*DAT_004eff00);
      if (iVar11 < 1) {
        uVar6 = FUN_00498668(*puVar1);
        *(undefined4 *)(iVar8 * 0x18 + iVar5 + 8) = uVar6;
        FUN_00498680(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 8),DAT_004efef8);
        FUN_0043f506(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 8),0x18);
        FUN_0043f568(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 8),0x18);
        FUN_0043f0e0(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 8),0x14);
        FUN_0043f142(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 8),iVar12 + 0x22);
        FUN_0043ded4(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 8),0x10000);
        FUN_0043dfa4(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 8),0x10);
        uVar6 = FUN_00499416(*puVar1);
        *(undefined4 *)(iVar8 * 0x18 + iVar5 + 0xc) = uVar6;
        FUN_0043f506(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0xc),0x1fb);
        FUN_0043f568(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0xc),0x1c);
        FUN_0043f0e0(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0xc),0x34);
        FUN_0043f142(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0xc),iVar12 + 0x20);
        FUN_00499678(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0xc),1);
        FUN_0049942e(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0xc),(int)puVar2 + iVar8 * 0x210 + 0x1cf
                    );
        FUN_0044143e(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0xc),*DAT_004efca8,0);
        uVar6 = FUN_0044104c(0xffffff);
        FUN_0044140e(*(undefined4 *)(iVar5 + iVar8 * 0x18 + 0xc),uVar6,0);
        iVar12 = iVar12 + 0x54;
      }
      else {
        uVar6 = FUN_00498668(*puVar1);
        *(undefined4 *)(iVar8 * 0x18 + iVar5 + 8) = uVar6;
        FUN_00498680(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 8),DAT_004eff04);
        FUN_0043f506(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 8),0x18);
        FUN_0043f568(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 8),0x18);
        FUN_0043f0e0(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 8),0x14);
        FUN_0043f142(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 8),iVar12 + 0x22);
        FUN_0043ded4(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 8),0x10000);
        FUN_0043dfa4(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 8),0x10);
        uVar6 = FUN_00499416(*puVar1);
        *(undefined4 *)(iVar8 * 0x18 + iVar5 + 0xc) = uVar6;
        FUN_0043f506(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0xc),0x1fb);
        FUN_0043f568(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0xc),0x1c);
        FUN_0043f0e0(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0xc),0x34);
        FUN_0043f142(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0xc),iVar12 + 0x20);
        FUN_00499678(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0xc),1);
        FUN_0049942e(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0xc),puVar2 + iVar8 * 0x108 + 0x5a);
        uVar6 = FUN_0044104c(0xffffff);
        FUN_0044140e(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0xc),uVar6,0);
        FUN_0044143e(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0xc),*DAT_004efca8,0);
        uVar6 = FUN_00498668(*puVar1);
        *(undefined4 *)(iVar8 * 0x18 + iVar5 + 0x10) = uVar6;
        FUN_00498680(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0x10),DAT_004efef8);
        FUN_0043f506(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0x10),0x18);
        FUN_0043f568(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0x10),0x18);
        FUN_0043f0e0(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0x10),0x14);
        FUN_0043f142(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0x10),iVar12 + 0x3e);
        FUN_0043ded4(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0x10),0x10000);
        FUN_0043dfa4(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0x10),0x10);
        uVar6 = FUN_00499416(*puVar1);
        *(undefined4 *)(iVar8 * 0x18 + iVar5 + 0x14) = uVar6;
        FUN_0043f506(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0x14),0x1fb);
        FUN_0043f568(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0x14),0x1c);
        FUN_0043f0e0(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0x14),0x34);
        FUN_0043f142(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0x14),iVar12 + 0x3c);
        FUN_00499678(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0x14),1);
        FUN_0049942e(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0x14),
                     (int)puVar2 + iVar8 * 0x210 + 0x1cf);
        FUN_0044143e(*(undefined4 *)(iVar8 * 0x18 + iVar5 + 0x14),*DAT_004efca8,0);
        uVar6 = FUN_0044104c(0xffffff);
        FUN_0044140e(*(undefined4 *)(iVar5 + iVar8 * 0x18 + 0x14),uVar6,0);
        iVar12 = iVar12 + 0x70;
      }
    }
    FUN_0043f568(*puVar1,iVar12);
    piVar4 = DAT_004efef4;
    *DAT_004efef4 = iVar12;
    piVar3 = DAT_004efef0;
    *DAT_004efef0 = 0;
    if (0x100 < *piVar4) {
      iVar8 = 0x10000 / *piVar4;
      if (iVar8 < 0x14) {
        iVar8 = 0x14;
      }
      iVar12 = FUN_0043de82(*DAT_004efeec);
      *piVar3 = iVar12;
      if (*piVar3 != 0) {
        FUN_0043f4c0(*piVar3,2,iVar8);
        FUN_0043f09a(*piVar3,0x234,0);
        uVar6 = FUN_0044104c(DAT_004eff08);
        FUN_0044127e(*piVar3,uVar6,0);
        FUN_0044129e(*piVar3,0x7f,0);
        FUN_0044131c(*piVar3,0,0);
        FUN_0044146a(*piVar3,1,0);
        FUN_004ed7d8(*piVar3,0,0);
        FUN_0043dfa4(*piVar3,0x10);
      }
    }
  }
  return;
}

