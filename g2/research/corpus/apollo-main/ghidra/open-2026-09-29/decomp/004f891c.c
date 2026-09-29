
undefined4 FUN_004f891c(int param_1)

{
  int *piVar1;
  ushort *puVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  int iVar10;
  ushort uVar11;
  int iVar12;
  int iVar13;
  int local_2c;
  int local_28;
  
  piVar1 = DAT_004f9348;
  *DAT_004f9348 = param_1;
  uVar4 = FUN_0043de82(*(undefined4 *)(DAT_004f934c + *piVar1 * 8 + 4));
  FUN_0043f09a(uVar4,0x14,0x10);
  FUN_0043f506(uVar4,0x13b);
  FUN_0043f568(uVar4,0x100);
  uVar5 = FUN_0044104c(0);
  FUN_0044127e(uVar4,uVar5,0);
  FUN_0044129e(uVar4,0,0);
  FUN_0044131c(uVar4,0,0);
  FUN_0044133a(uVar4,0,0);
  FUN_00441378(uVar4,0,0);
  FUN_00441386(uVar4,0,0);
  FUN_004413b0(uVar4,0,0);
  FUN_00441394(uVar4,0,0);
  FUN_004413a2(uVar4,0,0);
  FUN_004f5068(uVar4,0,0);
  FUN_0044146a(uVar4,0,0);
  uVar5 = FUN_0044104c(0);
  FUN_004412ec(uVar4,uVar5,0);
  uVar5 = FUN_0044104c(0xffffff);
  FUN_0044140e(uVar4,uVar5,0);
  FUN_0044142e(uVar4,0xff,0);
  FUN_0043dfa4(uVar4,0x12);
  *DAT_004f92e0 = 1;
  puVar2 = DAT_004f9350;
  if (*DAT_004f9350 == 0) {
    uVar5 = FUN_0043de82(uVar4);
    FUN_0043f4c0(uVar5,0x3fffffff,0x3fffffff);
    FUN_0043f6b8(uVar5,9,0,0);
    uVar4 = FUN_0044104c(0);
    FUN_0044127e(uVar5,uVar4,0);
    FUN_0044129e(uVar5,0,0);
    FUN_0044131c(uVar5,0,0);
    FUN_0044133a(uVar5,0,0);
    FUN_00441378(uVar5,0,0);
    FUN_00441386(uVar5,0,0);
    FUN_004413b0(uVar5,0,0);
    FUN_004f5068(uVar5,0,0);
    FUN_0044146a(uVar5,0,0);
    uVar4 = FUN_0044104c(0);
    FUN_004412ec(uVar5,uVar4,0);
    uVar4 = FUN_0044104c(0xffffff);
    FUN_0044140e(uVar5,uVar4,0);
    FUN_0044142e(uVar5,0xff,0);
    FUN_0043dfa4(uVar5,0x12);
    uVar6 = FUN_0043de82(uVar5);
    FUN_0043f4c0(uVar6,0x3fffffff,0x3fffffff);
    FUN_0043f6b8(uVar6,2,0,0);
    uVar4 = FUN_0044104c(0);
    FUN_0044127e(uVar6,uVar4,0);
    FUN_0044129e(uVar6,0,0);
    FUN_0044131c(uVar6,0,0);
    FUN_0044133a(uVar6,0,0);
    FUN_00441378(uVar6,0,0);
    FUN_00441386(uVar6,0,0);
    FUN_004413b0(uVar6,0,0);
    FUN_004f5068(uVar6,0,0);
    FUN_0044146a(uVar6,0,0);
    uVar4 = FUN_0044104c(0);
    FUN_004412ec(uVar6,uVar4,0);
    uVar4 = FUN_0044104c(0xffffff);
    FUN_0044140e(uVar6,uVar4,0);
    FUN_0044142e(uVar6,0xff,0);
    FUN_0043dfa4(uVar6,0x12);
    uVar7 = FUN_00498668(uVar6);
    FUN_00498680(uVar7,DAT_004f9470);
    FUN_0043f506(uVar7,0x18);
    FUN_0043f568(uVar7,0x18);
    FUN_0043f6b8(uVar7,1,0,2);
    FUN_0043ded4(uVar7,0x10000);
    FUN_0043dfa4(uVar7,0x10);
    uVar8 = FUN_00499416(uVar6);
    uVar4 = FUN_0044104c(0xffffff);
    FUN_0044140e(uVar8,uVar4,0);
    uVar4 = DAT_004f9474;
    uVar9 = FUN_00460084(DAT_004f9474);
    uVar4 = FUN_0045fffe(uVar4,uVar9);
    FUN_0049942e(uVar8,uVar4);
    puVar3 = DAT_004f9478;
    FUN_0044143e(uVar8,*DAT_004f9478,0);
    FUN_0043f6d6(uVar8,uVar7,0x14,8,0);
    uVar5 = FUN_00499416(uVar5);
    FUN_0043f506(uVar5,0x13b);
    FUN_0043f568(uVar5,0x3fffffff);
    FUN_0043f6d6(uVar5,uVar6,0xe,0,4);
    uVar4 = FUN_0044104c(0xffffff);
    FUN_0044140e(uVar5,uVar4,0);
    uVar4 = DAT_004f947c;
    uVar6 = FUN_00460084(DAT_004f947c);
    uVar4 = FUN_0045fffe(uVar4,uVar6);
    FUN_0049942e(uVar5,uVar4);
    FUN_0044143e(uVar5,*puVar3,0);
    FUN_0044145a(uVar5,2,0);
  }
  else {
    iVar13 = 0;
    iVar12 = 0;
    local_28 = 0x100;
    for (uVar11 = 0; uVar11 < *puVar2; uVar11 = uVar11 + 1) {
      local_2c = 0;
      quicklist_lock_storage();
      FUN_004f50d6(puVar2 + (uint)uVar11 * 0x94 + 4,*DAT_004f9478,0x11b,0,0,2,&local_2c);
      quicklist_unlock_storage();
      iVar10 = local_2c;
      if (*(char *)((int)puVar2 + (uint)uVar11 * 0x128 + 0xd1) != '\0') {
        iVar10 = local_2c + 0x1c;
      }
      iVar10 = iVar10 + 0x14;
      if (local_28 < iVar10 + iVar13) {
        if (local_28 - iVar13 < 0x1c) break;
        uVar5 = FUN_00498668(uVar4);
        if (*(char *)((int)puVar2 + (uint)uVar11 * 0x128 + 0x129) == '\0') {
          FUN_00498680(uVar5,DAT_004f9be0);
        }
        else {
          FUN_00498680(uVar5,DAT_004f9480);
        }
        FUN_0043f506(uVar5,0x18);
        FUN_0043f568(uVar5,0x18);
        FUN_0043f0e0(uVar5,0);
        FUN_0043f142(uVar5,iVar13 + 2);
        if (local_28 - iVar13 < iVar10) {
          uVar4 = FUN_00499416(uVar4);
          FUN_0043f506(uVar4,0x11b);
          FUN_0043f568(uVar4,0x1c);
          FUN_0043f0e0(uVar4,0x20);
          FUN_0043f142(uVar4,iVar13);
          FUN_00499678(uVar4,1);
          quicklist_lock_storage();
          FUN_0049942e(uVar4,puVar2 + (uint)uVar11 * 0x94 + 4);
          quicklist_unlock_storage();
          uVar5 = FUN_0044104c(0xffffff);
          FUN_0044140e(uVar4,uVar5,0);
          FUN_0044143e(uVar4,*DAT_004f9478,0);
          break;
        }
      }
      uVar5 = FUN_00498668(uVar4);
      if (*(char *)((int)puVar2 + (uint)uVar11 * 0x128 + 0x129) == '\0') {
        FUN_00498680(uVar5,DAT_004f9be0);
      }
      else {
        FUN_00498680(uVar5,DAT_004f9480);
      }
      FUN_0043f506(uVar5,0x18);
      FUN_0043f568(uVar5,0x18);
      FUN_0043f0e0(uVar5,0);
      FUN_0043f142(uVar5,iVar13 + 2);
      uVar5 = FUN_00499416(uVar4);
      FUN_0043f506(uVar5,0x11b);
      FUN_0043f568(uVar5,local_2c);
      FUN_0043f0e0(uVar5,0x20);
      FUN_0043f142(uVar5,iVar13);
      quicklist_lock_storage();
      FUN_0049942e(uVar5,puVar2 + (uint)uVar11 * 0x94 + 4);
      quicklist_unlock_storage();
      uVar6 = FUN_0044104c(0xffffff);
      FUN_0044140e(uVar5,uVar6,0);
      FUN_0044143e(uVar5,*DAT_004f9478,0);
      FUN_00499678(uVar5,1);
      iVar13 = local_2c + iVar13;
      if ((*(int *)(puVar2 + (uint)uVar11 * 0x94 + 0x92) < 0) ||
         ((*(int *)(puVar2 + (uint)uVar11 * 0x94 + 0x92) < 1 &&
          (*(int *)(puVar2 + (uint)uVar11 * 0x94 + 0x90) == 0)))) {
        *(undefined1 *)((int)puVar2 + (uint)uVar11 * 0x128 + 0xd1) = 0;
      }
      else {
        uVar5 = FUN_00499416(uVar4);
        FUN_0043f506(uVar5,0x11b);
        FUN_0043f568(uVar5,0x1c);
        FUN_0043f0e0(uVar5,0x20);
        FUN_0043f142(uVar5,iVar13);
        FUN_00499678(uVar5,1);
        quicklist_lock_storage();
        FUN_004f5366(*(undefined4 *)(puVar2 + (uint)uVar11 * 0x94 + 0x90),
                     *(undefined4 *)(puVar2 + (uint)uVar11 * 0x94 + 0x92),
                     (char)puVar2[(uint)uVar11 * 0x94 + 0x94],
                     (int)puVar2 + (uint)uVar11 * 0x128 + 0xd1,0x40);
        FUN_0049942e(uVar5,(int)puVar2 + (uint)uVar11 * 0x128 + 0xd1);
        quicklist_unlock_storage();
        uVar6 = FUN_0044104c(0xffffff);
        FUN_0044140e(uVar5,uVar6,0);
        FUN_0044143e(uVar5,*DAT_004f9478,0);
        iVar13 = iVar13 + 0x1c;
      }
      iVar13 = iVar13 + 0x14;
      iVar12 = iVar12 + 1;
    }
    iVar13 = FUN_0043d0ce();
    if (iVar13 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004f9bd8,DAT_004f9af8,DAT_004f9af4,0xd7d,DAT_004f9af0,iVar12);
    }
    iVar13 = FUN_0043d0ce();
    if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004f9bdc,DAT_004f9bdc,iVar12);
    }
  }
  return 0;
}

