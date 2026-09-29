
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong conversate_ui_menu_page_create
                   (char param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  undefined *puVar2;
  ushort *puVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int iVar6;
  uint uVar7;
  
  iVar1 = DAT_005b5cc8;
  puVar3 = (ushort *)FUN_005b43e8();
  if (param_1 == '\0') {
    uVar4 = FUN_0043de82(*_DAT_005b5cf8);
    *(undefined4 *)(iVar1 + 4) = uVar4;
    FUN_0043f4c0(*(undefined4 *)(iVar1 + 4),0x240,0x120);
    FUN_0043f09a(*(undefined4 *)(iVar1 + 4),0,0);
    FUN_0044129e(*(undefined4 *)(iVar1 + 4),0,0);
    FUN_0044131c(*(undefined4 *)(iVar1 + 4),0,0);
    FUN_0044146a(*(undefined4 *)(iVar1 + 4),0,0);
    FUN_005b5720(*(undefined4 *)(iVar1 + 4),0,0);
    FUN_0043dfa4(*(undefined4 *)(iVar1 + 4),0x10);
  }
  FUN_0044d878(*(undefined4 *)(iVar1 + 4));
  uVar4 = FUN_00499416(*(undefined4 *)(iVar1 + 4));
  puVar2 = PTR_s_ID_CONVERSATE_SELECT_PREP_NOTES_005b5d04;
  uVar5 = FUN_00460084(PTR_s_ID_CONVERSATE_SELECT_PREP_NOTES_005b5d04);
  uVar5 = FUN_0045fffe(puVar2,uVar5);
  FUN_0049942e(uVar4,uVar5);
  FUN_0043f4c0(uVar4,0x3fffffff,0x2c);
  FUN_0043f09a(uVar4,0xc,0);
  uVar5 = FUN_0044104c(0xffffff);
  FUN_0044140e(uVar4,uVar5,0);
  FUN_0044143e(uVar4,*_DAT_005b5d08,0);
  FUN_0044145a(uVar4,2,0);
  puVar2 = PTR_s_ID_CONVERSATE_SKIP_N_START_005b5d0c;
  uVar4 = FUN_00460084(PTR_s_ID_CONVERSATE_SKIP_N_START_005b5d0c);
  uVar4 = FUN_0045fffe(puVar2,uVar4);
  uVar4 = FUN_005b1150(*(undefined4 *)(iVar1 + 4),PTR_LAB_005b5d10,uVar4);
  *(undefined4 *)(iVar1 + 0x7c) = uVar4;
  FUN_0043f09a(*(undefined4 *)(iVar1 + 0x7c),0,0x3c);
  if (*puVar3 == 0) {
    *(undefined4 *)(iVar1 + 0x80) = *(undefined4 *)(iVar1 + 0x7c);
    *(undefined4 *)(iVar1 + 0x84) = 0xffffffff;
    FUN_005b1072(*(undefined4 *)(iVar1 + 0x80),1);
  }
  else {
    uVar4 = FUN_005b12ba(*(undefined4 *)(iVar1 + 4));
    *(undefined4 *)(iVar1 + 100) = uVar4;
    FUN_0043f09a(*(undefined4 *)(iVar1 + 100),0,100);
    for (uVar7 = 0; uVar7 < *puVar3; uVar7 = uVar7 + 1) {
      iVar6 = FUN_005b1150(*(undefined4 *)(iVar1 + 100),PTR_DAT_005b5d14,puVar3 + uVar7 * 0x44 + 5);
      if ((iVar6 != 0) && (*(int *)(puVar3 + 0x552) == *(int *)(puVar3 + uVar7 * 0x44 + 2))) {
        *(int *)(iVar1 + 0x80) = iVar6;
        *(uint *)(iVar1 + 0x84) = uVar7;
        FUN_005b1072(*(undefined4 *)(iVar1 + 0x80),1);
      }
    }
    if (*(int *)(iVar1 + 0x80) == 0) {
      *(undefined4 *)(iVar1 + 0x80) = *(undefined4 *)(iVar1 + 0x7c);
      *(undefined4 *)(iVar1 + 0x84) = 0xffffffff;
      FUN_005b1072(*(undefined4 *)(iVar1 + 0x80),1);
    }
    else {
      FUN_0044ea2e(*(undefined4 *)(iVar1 + 0x80),0);
    }
  }
  return (ulonglong)param_4 << 0x20;
}

