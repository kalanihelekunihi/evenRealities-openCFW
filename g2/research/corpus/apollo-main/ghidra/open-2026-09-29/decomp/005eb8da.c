
undefined4 FUN_005eb8da(void)

{
  undefined4 *puVar1;
  int *piVar2;
  int *piVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 in_r3;
  ushort uVar8;
  
  piVar3 = DAT_005ebc54;
  piVar2 = DAT_005ebc34;
  if ((((*DAT_005ebc54 != 0) && (DAT_005ebc34[0x85] == 0)) &&
      (iVar4 = td_session_struct_ptr(), iVar4 != 0)) && (*(short *)(iVar4 + 0x406) != 0)) {
    if (*piVar2 != 0) {
      FUN_00441488(*piVar2,0x33,0);
    }
    iVar5 = FUN_005e4f54(*piVar3,0);
    piVar2[0x85] = iVar5;
    FUN_0043f4c0(piVar2[0x85],0x22c,0x3fffffff);
    FUN_0044119c(piVar2[0x85],0x78,0);
    FUN_004411aa(piVar2[0x85],0x10a,0);
    FUN_0044120e(piVar2[0x85],8,0);
    FUN_0044122a(piVar2[0x85],8,0);
    FUN_00441238(piVar2[0x85],8,0);
    FUN_0044121c(piVar2[0x85],8,0);
    FUN_00441246(piVar2[0x85],4,0);
    FUN_0048ba78(piVar2[0x85],1);
    FUN_0048ba92(piVar2[0x85],0,0,0);
    FUN_0044e3ca(piVar2[0x85],0xc);
    FUN_0044e368(piVar2[0x85],0);
    uVar6 = FUN_0043de82(piVar2[0x85]);
    FUN_0043f4c0(uVar6,0x21c,0x3fffffff);
    FUN_0043dfa4(uVar6,0x10);
    FUN_0044129e(uVar6,0,0);
    FUN_0044131c(uVar6,0,0);
    FUN_005eb2bc(uVar6,0,0);
    FUN_00441262(uVar6,6,0);
    iVar5 = FUN_00499416(uVar6);
    piVar2[0x86] = iVar5;
    FUN_0043f506(piVar2[0x86],0x21c);
    FUN_0049942e(piVar2[0x86],iVar4 + 6);
    FUN_00499678(piVar2[0x86],0);
    uVar6 = FUN_0044104c(0xffffff);
    FUN_0044140e(piVar2[0x86],uVar6,0);
    FUN_0044145a(piVar2[0x86],1,0);
    puVar1 = DAT_005ebc2c;
    FUN_0044143e(piVar2[0x86],*DAT_005ebc2c,0);
    iVar5 = FUN_0043de82(piVar2[0x85]);
    piVar2[0x87] = iVar5;
    FUN_0043f4c0(piVar2[0x87],0x208,0x3fffffff);
    FUN_0043dfa4(piVar2[0x87],0x10);
    FUN_0044129e(piVar2[0x87],0,0);
    FUN_0044131c(piVar2[0x87],0,0);
    FUN_005eb2bc(piVar2[0x87],0,0);
    FUN_00441246(piVar2[0x87],2,0);
    FUN_00441270(piVar2[0x87],0x14,0);
    FUN_0048ba78(piVar2[0x87],1);
    FUN_0048ba92(piVar2[0x87],0,0,0);
    *(undefined1 *)((int)piVar2 + 0x279) = 0;
    *(undefined1 *)(piVar2 + 0x9f) = 0;
    for (uVar8 = 0; uVar8 < *(ushort *)(iVar4 + 0x406); uVar8 = uVar8 + 1) {
      uVar7 = FUN_00499416(piVar2[0x87]);
      FUN_0043f506(uVar7,0x208);
      FUN_00499678(uVar7,0);
      FUN_0049942e(uVar7,iVar4 + (uint)uVar8 * 0x88 + 0x40e);
      uVar6 = DAT_005ebc30;
      if (uVar8 == 0) {
        uVar6 = 0xffffff;
      }
      uVar6 = FUN_0044104c(uVar6);
      FUN_0044140e(uVar7,uVar6,0);
      FUN_0044143e(uVar7,*puVar1,0);
    }
    iVar4 = FUN_00498668(piVar2[0x85]);
    piVar2[0x88] = iVar4;
    FUN_00498680(piVar2[0x88],DAT_005ebc58);
    FUN_0043ded4(piVar2[0x88],0x20000);
    FUN_0043f66c(piVar2[0x85]);
    FUN_0044ea04(piVar2[0x85],0,0);
    FUN_005eb3c6(piVar2);
    uVar6 = td_counter_b_get();
    FUN_005e5484(4,uVar6,3);
  }
  return in_r3;
}

