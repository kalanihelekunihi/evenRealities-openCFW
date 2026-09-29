
undefined4 FUN_004f9484(void)

{
  undefined4 *puVar1;
  int *piVar2;
  ushort *puVar3;
  undefined4 *puVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  undefined4 in_r3;
  ushort uVar12;
  
  piVar2 = DAT_004f9f0c;
  if ((*DAT_004f9f0c != 0) &&
     (iVar5 = FUN_0043e2ea(*DAT_004f9f0c), puVar3 = DAT_004fa04c, iVar5 != 0)) {
    if (*DAT_004fa04c == 0) {
      uVar6 = FUN_0043de82(*piVar2);
      FUN_0043f4c0(uVar6,0x3fffffff,0x3fffffff);
      FUN_0043f6b8(uVar6,9,0,0);
      uVar7 = FUN_0044104c(0);
      FUN_0044127e(uVar6,uVar7,0);
      FUN_0044129e(uVar6,0,0);
      FUN_0044131c(uVar6,0,0);
      FUN_0044133a(uVar6,0,0);
      FUN_00441378(uVar6,0,0);
      FUN_00441386(uVar6,0,0);
      FUN_004413b0(uVar6,0,0);
      FUN_004f5068(uVar6,0,0);
      FUN_0044146a(uVar6,0,0);
      uVar7 = FUN_0044104c(0);
      FUN_004412ec(uVar6,uVar7,0);
      uVar7 = FUN_0044104c(0xffffff);
      FUN_0044140e(uVar6,uVar7,0);
      FUN_0044142e(uVar6,0xff,0);
      FUN_0043dfa4(uVar6,0x12);
      uVar8 = FUN_0043de82(uVar6);
      FUN_0043f4c0(uVar8,0x3fffffff,0x3fffffff);
      FUN_0043f6b8(uVar8,2,0,0);
      uVar7 = FUN_0044104c(0);
      FUN_0044127e(uVar8,uVar7,0);
      FUN_0044129e(uVar8,0,0);
      FUN_0044131c(uVar8,0,0);
      FUN_0044133a(uVar8,0,0);
      FUN_00441378(uVar8,0,0);
      FUN_00441386(uVar8,0,0);
      FUN_004413b0(uVar8,0,0);
      FUN_004f5068(uVar8,0,0);
      FUN_0044146a(uVar8,0,0);
      uVar7 = FUN_0044104c(0);
      FUN_004412ec(uVar8,uVar7,0);
      uVar7 = FUN_0044104c(0xffffff);
      FUN_0044140e(uVar8,uVar7,0);
      FUN_0044142e(uVar8,0xff,0);
      FUN_0043dfa4(uVar8,0x12);
      uVar9 = FUN_00498668(uVar8);
      FUN_00498680(uVar9,DAT_004fa050);
      FUN_0043f506(uVar9,0x18);
      FUN_0043f568(uVar9,0x18);
      FUN_0043f6b8(uVar9,1,0,2);
      FUN_0043ded4(uVar9,0x10000);
      FUN_0043dfa4(uVar9,0x10);
      uVar10 = FUN_00499416(uVar8);
      uVar7 = FUN_0044104c(0xffffff);
      FUN_0044140e(uVar10,uVar7,0);
      uVar7 = DAT_004fa054;
      uVar11 = FUN_00460084(DAT_004fa054);
      uVar7 = FUN_0045fffe(uVar7,uVar11);
      FUN_0049942e(uVar10,uVar7);
      puVar1 = DAT_004fa29c;
      FUN_0044143e(uVar10,*DAT_004fa29c,0);
      FUN_0043f6d6(uVar10,uVar9,0x14,8,0);
      uVar6 = FUN_00499416(uVar6);
      FUN_0043f506(uVar6,0x222);
      FUN_0043f568(uVar6,0x3fffffff);
      in_r3 = 4;
      FUN_0043f6d6(uVar6,uVar8,0xe,0);
      uVar7 = FUN_0044104c(0xffffff);
      FUN_0044140e(uVar6,uVar7,0);
      uVar7 = DAT_004fa2a0;
      uVar8 = FUN_00460084(DAT_004fa2a0);
      uVar7 = FUN_0045fffe(uVar7,uVar8);
      FUN_0049942e(uVar6,uVar7);
      FUN_0044143e(uVar6,*puVar1,0);
      FUN_0044145a(uVar6,2,0);
    }
    else {
      for (uVar12 = 0; puVar1 = DAT_004f9f08, uVar12 < *puVar3; uVar12 = uVar12 + 1) {
        uVar7 = FUN_0043de82(*piVar2);
        puVar1[(uint)uVar12 * 4] = uVar7;
        FUN_0043f506(puVar1[(uint)uVar12 * 4],0x222);
        FUN_0043f568(puVar1[(uint)uVar12 * 4],0x3fffffff);
        if (uVar12 == 0) {
          FUN_0043f6b8(*puVar1,1,0,0);
        }
        else {
          FUN_0043f6d6(puVar1[(uint)uVar12 * 4],puVar1[(uint)uVar12 * 4 + -4],0xd,0,4);
        }
        FUN_00441488(puVar1[(uint)uVar12 * 4],0xff,0);
        uVar7 = FUN_0044104c(0);
        FUN_0044127e(puVar1[(uint)uVar12 * 4],uVar7,0);
        FUN_0044129e(puVar1[(uint)uVar12 * 4],0,0);
        FUN_0044146a(puVar1[(uint)uVar12 * 4],6,0);
        uVar7 = FUN_0044104c(0);
        FUN_004412ec(puVar1[(uint)uVar12 * 4],uVar7,0);
        FUN_0044131c(puVar1[(uint)uVar12 * 4],0,0);
        FUN_0044120e(puVar1[(uint)uVar12 * 4],8,0);
        FUN_0044121c(puVar1[(uint)uVar12 * 4],8,0);
        FUN_0044122a(puVar1[(uint)uVar12 * 4],8,0);
        FUN_00441238(puVar1[(uint)uVar12 * 4],5,0);
        FUN_0044e368(puVar1[(uint)uVar12 * 4],0);
        FUN_0043dfa4(puVar1[(uint)uVar12 * 4],0x10);
        uVar7 = FUN_00498668(puVar1[(uint)uVar12 * 4]);
        puVar1[(uint)uVar12 * 4 + 1] = uVar7;
        if (*(char *)((int)puVar3 + (uint)uVar12 * 0x128 + 0x129) == '\0') {
          FUN_00498680(puVar1[(uint)uVar12 * 4 + 1],DAT_004f9be0);
          FUN_00441488(puVar1[(uint)uVar12 * 4],0xff,0);
        }
        else {
          FUN_00498680(puVar1[(uint)uVar12 * 4 + 1],DAT_004fa700);
          FUN_00441488(puVar1[(uint)uVar12 * 4],0x30,0);
        }
        FUN_0043f506(puVar1[(uint)uVar12 * 4 + 1],0x18);
        FUN_0043f568(puVar1[(uint)uVar12 * 4 + 1],0x18);
        FUN_0043f6b8(puVar1[(uint)uVar12 * 4 + 1],1,0,2);
        uVar7 = FUN_00499416(puVar1[(uint)uVar12 * 4]);
        puVar1[(uint)uVar12 * 4 + 2] = uVar7;
        FUN_0043f506(puVar1[(uint)uVar12 * 4 + 2],0x1f5);
        FUN_0043f568(puVar1[(uint)uVar12 * 4 + 2],0x3fffffff);
        in_r3 = 0xfffffffe;
        FUN_0043f6d6(puVar1[(uint)uVar12 * 4 + 2],puVar1[(uint)uVar12 * 4 + 1],0x13,8);
        FUN_00499678(puVar1[(uint)uVar12 * 4 + 2],0);
        uVar7 = FUN_0044104c(0xffffff);
        FUN_0044140e(puVar1[(uint)uVar12 * 4 + 2],uVar7,0);
        puVar4 = DAT_004fa29c;
        FUN_0044143e(puVar1[(uint)uVar12 * 4 + 2],*DAT_004fa29c,0);
        quicklist_lock_storage();
        FUN_0049942e(puVar1[(uint)uVar12 * 4 + 2],puVar3 + (uint)uVar12 * 0x94 + 4);
        quicklist_unlock_storage();
        if ((*(int *)(puVar3 + (uint)uVar12 * 0x94 + 0x92) < 0) ||
           ((*(int *)(puVar3 + (uint)uVar12 * 0x94 + 0x92) < 1 &&
            (*(int *)(puVar3 + (uint)uVar12 * 0x94 + 0x90) == 0)))) {
          *(undefined1 *)((int)puVar3 + (uint)uVar12 * 0x128 + 0xd1) = 0;
        }
        else {
          uVar7 = FUN_00499416(puVar1[(uint)uVar12 * 4]);
          puVar1[(uint)uVar12 * 4 + 3] = uVar7;
          FUN_0043f506(puVar1[(uint)uVar12 * 4 + 3],0x1f5);
          FUN_0043f568(puVar1[(uint)uVar12 * 4 + 3],0x1c);
          FUN_0043f6d6(puVar1[(uint)uVar12 * 4 + 3],puVar1[(uint)uVar12 * 4 + 2],0xd,0,0);
          FUN_00499678(puVar1[(uint)uVar12 * 4 + 3],1);
          quicklist_lock_storage();
          in_r3 = 0x40;
          FUN_004f5366(*(undefined4 *)(puVar3 + (uint)uVar12 * 0x94 + 0x90),
                       *(undefined4 *)(puVar3 + (uint)uVar12 * 0x94 + 0x92),
                       (char)puVar3[(uint)uVar12 * 0x94 + 0x94],
                       (int)puVar3 + (uint)uVar12 * 0x128 + 0xd1);
          FUN_0049942e(puVar1[(uint)uVar12 * 4 + 3],(int)puVar3 + (uint)uVar12 * 0x128 + 0xd1);
          quicklist_unlock_storage();
          uVar7 = FUN_0044104c(0xffffff);
          FUN_0044140e(puVar1[(uint)uVar12 * 4 + 3],uVar7,0);
          FUN_0044143e(puVar1[(uint)uVar12 * 4 + 3],*puVar4,0);
        }
      }
      FUN_004f9368();
    }
  }
  return in_r3;
}

