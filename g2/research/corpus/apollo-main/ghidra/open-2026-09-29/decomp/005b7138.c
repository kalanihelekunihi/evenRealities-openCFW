
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_005b7138(void)

{
  int iVar1;
  undefined *puVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  int iVar8;
  undefined4 in_r3;
  undefined2 auStack_44 [2];
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  
  iVar1 = DAT_005b7604;
  uStack_20 = in_r3;
  FUN_0043c0e4(auStack_44,0x24,0);
  *(undefined4 *)(iVar1 + 0x24) = 0;
  *(undefined4 *)(iVar1 + 0x28) = 0;
  *(undefined4 *)(iVar1 + 0x2c) = 0;
  *(undefined2 *)(iVar1 + 0x60) = 0;
  FUN_0043c0e4(iVar1 + 0x30,0x30,0);
  if (*(int *)(iVar1 + 0x1c) == 0) {
    uVar3 = FUN_0043de82(*_DAT_005b765c);
    *(undefined4 *)(iVar1 + 0x1c) = uVar3;
  }
  else {
    FUN_0044d878(*(undefined4 *)(iVar1 + 0x1c));
  }
  FUN_0043f09a(*(undefined4 *)(iVar1 + 0x1c),0,0);
  FUN_0044129e(*(undefined4 *)(iVar1 + 0x1c),0,0);
  FUN_0044131c(*(undefined4 *)(iVar1 + 0x1c),1,0);
  FUN_0044130c(*(undefined4 *)(iVar1 + 0x1c),0xff,0);
  uVar3 = FUN_0044104c(0xffffff);
  FUN_004412ec(*(undefined4 *)(iVar1 + 0x1c),uVar3,0);
  FUN_0044146a(*(undefined4 *)(iVar1 + 0x1c),6,0);
  FUN_0044122a(*(undefined4 *)(iVar1 + 0x1c),0xc,0);
  FUN_00441238(*(undefined4 *)(iVar1 + 0x1c),0,0);
  FUN_0044120e(*(undefined4 *)(iVar1 + 0x1c),0,0);
  FUN_0044121c(*(undefined4 *)(iVar1 + 0x1c),6,0);
  FUN_0043dfa4(*(undefined4 *)(iVar1 + 0x1c),0x10);
  uVar4 = FUN_0043de82(*(undefined4 *)(iVar1 + 0x1c));
  FUN_0043f4c0(uVar4,0x228,0x28);
  FUN_0043f09a(uVar4,0,0);
  FUN_0044129e(uVar4,0,0);
  FUN_0044131c(uVar4,0,0);
  FUN_0044146a(uVar4,0,0);
  FUN_005b69d4(uVar4,0,0);
  FUN_0043dfa4(uVar4,0x10);
  uVar5 = FUN_00498668(uVar4);
  FUN_00498680(uVar5,_DAT_005b7660);
  uVar3 = FUN_0044104c(0);
  FUN_0044127e(uVar5,uVar3,0);
  FUN_0044129e(uVar5,0xff,0);
  FUN_004413ce(uVar5,0xff,0);
  FUN_0043f6ac(uVar5,7);
  uVar6 = FUN_00499416(uVar4);
  uVar3 = _DAT_005b7664;
  uVar7 = FUN_00460084(_DAT_005b7664);
  uVar3 = FUN_0045fffe(uVar3,uVar7);
  FUN_0049942e(uVar6,uVar3);
  FUN_0044143e(uVar6,*DAT_005b7630,0);
  FUN_0043f4c0(uVar6,0x1e6,0x3fffffff);
  FUN_00499678(uVar6,1);
  FUN_0044145a(uVar6,1,0);
  uVar3 = FUN_0044104c(0xffffff);
  FUN_0044140e(uVar6,uVar3,0);
  FUN_0043f6d6(uVar6,uVar5,0x14,8,0xffffffff);
  uVar3 = FUN_0043de82(*(undefined4 *)(iVar1 + 0x1c));
  *(undefined4 *)(iVar1 + 0x24) = uVar3;
  FUN_0043f6d6(*(undefined4 *)(iVar1 + 0x24),uVar4,0xd,0,10);
  FUN_0043f4c0(*(undefined4 *)(iVar1 + 0x24),0x220,0xe0);
  FUN_0044129e(*(undefined4 *)(iVar1 + 0x24),0,0);
  FUN_0044131c(*(undefined4 *)(iVar1 + 0x24),0,0);
  FUN_0044130c(*(undefined4 *)(iVar1 + 0x24),0,0);
  FUN_0044146a(*(undefined4 *)(iVar1 + 0x24),0,0);
  FUN_005b69d4(*(undefined4 *)(iVar1 + 0x24),0,0);
  FUN_0044e3ca(*(undefined4 *)(iVar1 + 0x24),0xc);
  FUN_0043dfa4(*(undefined4 *)(iVar1 + 0x24),0x360);
  FUN_0044e368(*(undefined4 *)(iVar1 + 0x24),0);
  FUN_0044129e(*(undefined4 *)(iVar1 + 0x24),0,0x10000);
  FUN_0044130c(*(undefined4 *)(iVar1 + 0x24),0,0x10000);
  FUN_004413be(*(undefined4 *)(iVar1 + 0x24),0,0x10000);
  uVar3 = _DAT_005b7668;
  FUN_0044129e(*(undefined4 *)(iVar1 + 0x24),0,_DAT_005b7668);
  FUN_0044130c(*(undefined4 *)(iVar1 + 0x24),0,uVar3);
  FUN_004413be(*(undefined4 *)(iVar1 + 0x24),0,uVar3);
  puVar2 = PTR_FUN_005b6c48_1_005b766c;
  FUN_00451740(*(undefined4 *)(iVar1 + 0x24),PTR_FUN_005b6c48_1_005b766c,0xc,0);
  FUN_00451740(*(undefined4 *)(iVar1 + 0x24),puVar2,0xf,0);
  FUN_00451740(*(undefined4 *)(iVar1 + 0x24),puVar2,0xe,0);
  uVar3 = FUN_0043de82(*(undefined4 *)(iVar1 + 0x1c));
  *(undefined4 *)(iVar1 + 0x2c) = uVar3;
  FUN_0043f4c0(*(undefined4 *)(iVar1 + 0x2c),2,0x1c);
  iVar8 = FUN_0043fe16(*(undefined4 *)(iVar1 + 0x1c));
  FUN_0043f0e0(*(undefined4 *)(iVar1 + 0x2c),iVar8 + -10);
  uVar3 = FUN_0044104c(0xffffff);
  FUN_0044127e(*(undefined4 *)(iVar1 + 0x2c),uVar3,0);
  FUN_0044129e(*(undefined4 *)(iVar1 + 0x2c),0xff,0);
  FUN_0044131c(*(undefined4 *)(iVar1 + 0x2c),0,0);
  FUN_0044146a(*(undefined4 *)(iVar1 + 0x2c),0,0);
  FUN_005b69d4(*(undefined4 *)(iVar1 + 0x2c),0,0);
  FUN_0043dfa4(*(undefined4 *)(iVar1 + 0x2c),0x10);
  FUN_0043ded4(*(undefined4 *)(iVar1 + 0x24),1);
  FUN_0043ded4(*(undefined4 *)(iVar1 + 0x2c),1);
  FUN_0043ded4(*(undefined4 *)(iVar1 + 0x7c),1);
  FUN_0058c426(*(undefined4 *)(iVar1 + 8),200,0);
  FUN_0043ded4(*(undefined4 *)(iVar1 + 0x20),1);
  FUN_0043dfa4(*(undefined4 *)(iVar1 + 0x1c),1);
  auStack_44[0] = 300;
  uStack_40 = 0;
  uStack_3c = 0;
  uStack_38 = 0;
  uStack_34 = 0;
  uStack_30 = FUN_0043fd9e(*(undefined4 *)(iVar1 + 0x7c));
  uStack_2c = 0x240;
  uStack_28 = FUN_0043fdda(*(undefined4 *)(iVar1 + 0x7c));
  uStack_24 = 0x120;
  *(undefined1 *)(iVar1 + 0x98) = 1;
  FUN_005b7704(*(undefined4 *)(iVar1 + 0x1c),auStack_44,PTR_FUN_005b7116_1_005b7670);
  return 0;
}

