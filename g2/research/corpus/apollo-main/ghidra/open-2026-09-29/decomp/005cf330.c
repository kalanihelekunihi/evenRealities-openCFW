
undefined4
semantic_pdt_distortion_screen_event
          (int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  
  puVar1 = DAT_005cf61c;
  if (param_1 == 2) {
    uVar3 = FUN_0043de82(param_4);
    *puVar1 = uVar3;
    FUN_0043dfa4(*puVar1,0x10);
    FUN_0043f506(*puVar1,0x280);
    FUN_0043f568(*puVar1,0x1e0);
    uVar3 = FUN_0044104c(0);
    FUN_0044127e(*puVar1,uVar3,0);
    FUN_0044129e(*puVar1,0xff,0);
    FUN_0044131c(*puVar1,0,0);
    semantic_zero_four_object_styles(*puVar1,0,0);
    uVar3 = FUN_0043de82(*puVar1);
    FUN_0043dfa4(uVar3,0x10);
    FUN_0043f09a(uVar3,0,0x32);
    FUN_0043f506(uVar3,0x23e);
    FUN_0043f568(uVar3,0xce);
    uVar4 = FUN_0044104c(0);
    FUN_0044127e(uVar3,uVar4,0);
    FUN_0044129e(uVar3,0,0);
    FUN_0044131c(uVar3,2,0);
    uVar4 = FUN_0044104c(0xffffff);
    FUN_004412ec(uVar3,uVar4,0);
    FUN_0044130c(uVar3,0xff,0);
    FUN_0044133a(uVar3,0,0);
    FUN_00441378(uVar3,0,0);
    FUN_00441386(uVar3,0,0);
    FUN_004413b0(uVar3,0,0);
    FUN_00441394(uVar3,0,0);
    FUN_004413a2(uVar3,0,0);
    semantic_zero_four_object_styles(uVar3,0,0);
    FUN_0044120e(uVar3,0,0);
    FUN_0044121c(uVar3,0,0);
    FUN_0044122a(uVar3,0,0);
    FUN_00441238(uVar3,0,0);
    FUN_0044146a(uVar3,0,0);
    uVar4 = FUN_0044104c(0xffffff);
    FUN_0044140e(uVar3,uVar4,0);
    FUN_0044142e(uVar3,0xff,0);
    uVar4 = FUN_0043de82(uVar3);
    FUN_0043f4c0(uVar4,0x3fffffff,0x3fffffff);
    FUN_0044129e(uVar4,0,0);
    FUN_0044131c(uVar4,0,0);
    semantic_zero_four_object_styles(uVar4,0,0);
    FUN_0048ba78(uVar4,1);
    FUN_0048ba92(uVar4,2,2,2);
    FUN_00441246(uVar4,8,0);
    FUN_0043f6b8(uVar4,9,0,0);
    uVar3 = FUN_0043de82(uVar4);
    FUN_0043f4c0(uVar3,0x3fffffff,0x3fffffff);
    FUN_0044129e(uVar3,0,0);
    FUN_0044131c(uVar3,0,0);
    semantic_zero_four_object_styles(uVar3,0,0);
    FUN_0048ba78(uVar3,0);
    FUN_0048ba92(uVar3,2,2,2);
    FUN_00441254(uVar3,8,0);
    uVar5 = FUN_00498668(uVar3);
    FUN_00498680(uVar5,DAT_005cf620);
    FUN_0043f506(uVar5,0x18);
    FUN_0043f568(uVar5,0x18);
    FUN_0043ded4(uVar5,0x10000);
    FUN_0043dfa4(uVar5,0x10);
    uVar5 = FUN_00499416(uVar3);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_0044140e(uVar5,uVar3,0);
    uVar3 = DAT_005cf624;
    uVar6 = FUN_00460084(DAT_005cf624);
    uVar3 = FUN_0045fffe(uVar3,uVar6);
    FUN_0049942e(uVar5,uVar3);
    puVar2 = DAT_005cf628;
    FUN_0044143e(uVar5,*DAT_005cf628,0);
    uVar4 = FUN_00499416(uVar4);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_0044140e(uVar4,uVar3,0);
    uVar3 = DAT_005cf62c;
    uVar5 = FUN_00460084(DAT_005cf62c);
    uVar3 = FUN_0045fffe(uVar3,uVar5);
    FUN_0049942e(uVar4,uVar3);
    FUN_0044143e(uVar4,*puVar2,0);
    FUN_0044145a(uVar4,2,0);
    *(undefined4 *)(DAT_005cf630 + 4) = *puVar1;
  }
  return 0;
}

