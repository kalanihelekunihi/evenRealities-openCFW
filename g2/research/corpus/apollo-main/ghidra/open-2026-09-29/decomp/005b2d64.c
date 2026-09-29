
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_005b2d64(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int *piVar2;
  undefined *puVar3;
  short *psVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  uint uVar8;
  
  iVar5 = _DAT_005b3514;
  uVar8 = param_2;
  psVar4 = (short *)func_0x005b4766();
  if (*_DAT_005b3518 == '\x01') {
    if (*(int *)(iVar5 + 0xc) != 0) {
      FUN_0044d7b8(*(undefined4 *)(iVar5 + 0xc));
      *(undefined4 *)(iVar5 + 0xc) = 0;
    }
    if (*(int *)(iVar5 + 4) != 0) {
      FUN_0044d7b8(*(undefined4 *)(iVar5 + 4));
      *(undefined4 *)(iVar5 + 4) = 0;
      *(undefined4 *)(iVar5 + 0x84) = 0;
      *(undefined4 *)(iVar5 + 0x80) = 0;
      *(undefined4 *)(iVar5 + 0x7c) = 0;
      *(undefined4 *)(iVar5 + 100) = 0;
    }
    puVar1 = _DAT_005b3530;
    uVar6 = FUN_0043de82(*_DAT_005b3530);
    *(undefined4 *)(iVar5 + 8) = uVar6;
    FUN_0043f4c0(*(undefined4 *)(iVar5 + 8),0x240,0xcc);
    FUN_0043f6b8(*(undefined4 *)(iVar5 + 8),2,0,0);
    FUN_0044129e(*(undefined4 *)(iVar5 + 8),0,0);
    FUN_0044131c(*(undefined4 *)(iVar5 + 8),0,0);
    FUN_0044146a(*(undefined4 *)(iVar5 + 8),0,0);
    func_0x005b22bc(*(undefined4 *)(iVar5 + 8),0,0);
    FUN_0043dfa4(*(undefined4 *)(iVar5 + 8),0x70);
    uVar6 = FUN_0043de82(*(undefined4 *)(iVar5 + 8));
    *(undefined4 *)(iVar5 + 0x10) = uVar6;
    FUN_0043f4c0(*(undefined4 *)(iVar5 + 0x10),0x3fffffff,0x1c);
    FUN_0043f6b8(*(undefined4 *)(iVar5 + 0x10),3,0xfffffff4,8);
    FUN_0044129e(*(undefined4 *)(iVar5 + 0x10),0,0);
    FUN_0044131c(*(undefined4 *)(iVar5 + 0x10),0,0);
    FUN_0044146a(*(undefined4 *)(iVar5 + 0x10),0,0);
    func_0x005b22bc(*(undefined4 *)(iVar5 + 0x10),0,0);
    uVar6 = FUN_0058c7a0(*(undefined4 *)(iVar5 + 0x10),_DAT_005b3534);
    *(undefined4 *)(iVar5 + 0x18) = uVar6;
    FUN_0043f4c0(*(undefined4 *)(iVar5 + 0x18),0x3fffffff,0x3fffffff);
    FUN_0043f6b8(*(undefined4 *)(iVar5 + 0x18),7,0,0);
    FUN_00441488(*(undefined4 *)(iVar5 + 0x18),0x33,0);
    uVar6 = FUN_00499416(*(undefined4 *)(iVar5 + 0x10));
    *(undefined4 *)(iVar5 + 0x14) = uVar6;
    FUN_0043f4c0(*(undefined4 *)(iVar5 + 0x14),0x3fffffff,0x3fffffff);
    piVar2 = _DAT_005b3538;
    FUN_0044143e(*(undefined4 *)(iVar5 + 0x14),*_DAT_005b3538,0);
    uVar6 = FUN_0044104c(_DAT_005b353c);
    FUN_0044140e(*(undefined4 *)(iVar5 + 0x14),uVar6,0);
    FUN_0044145a(*(undefined4 *)(iVar5 + 0x14),2,0);
    uVar8 = 0;
    FUN_0043f6d6(*(undefined4 *)(iVar5 + 0x14),*(undefined4 *)(iVar5 + 0x18),0x14,8);
    func_0x005b22fa(*(undefined4 *)(iVar5 + 0x14),param_2);
    *(uint *)(iVar5 + 0x9c) = param_2 / 0x3c;
    uVar6 = FUN_005b12ba(*(undefined4 *)(iVar5 + 8));
    *(undefined4 *)(iVar5 + 100) = uVar6;
    puVar3 = PTR_s_ID_CONVERSATE_PREP_NOTES_005b3540;
    if ((*psVar4 == 0) || (*(int *)(psVar4 + 0x42) == 0)) {
      FUN_0043f6b8(*(undefined4 *)(iVar5 + 100),2,0,0);
    }
    else {
      uVar6 = FUN_00460084(PTR_s_ID_CONVERSATE_PREP_NOTES_005b3540);
      uVar6 = FUN_0045fffe(puVar3,uVar6);
      uVar6 = FUN_005b1150(*(undefined4 *)(iVar5 + 8),PTR_DAT_005b3544,uVar6);
      *(undefined4 *)(iVar5 + 0x7c) = uVar6;
      FUN_0043f6b8(*(undefined4 *)(iVar5 + 0x7c),1,0,0);
      uVar8 = 0;
      FUN_0043f6d6(*(undefined4 *)(iVar5 + 100),*(undefined4 *)(iVar5 + 0x7c),0xd,0);
    }
    uVar6 = FUN_0043de82(*puVar1);
    *(undefined4 *)(iVar5 + 0x20) = uVar6;
    FUN_0043f4c0(*(undefined4 *)(iVar5 + 0x20),0x240,0x3fffffff);
    FUN_004411aa(*(undefined4 *)(iVar5 + 0x20),0x54,0);
    FUN_0043f6b8(*(undefined4 *)(iVar5 + 0x20),5,0,0);
    FUN_0044129e(*(undefined4 *)(iVar5 + 0x20),0,0);
    FUN_0044131c(*(undefined4 *)(iVar5 + 0x20),0,0);
    FUN_0044146a(*(undefined4 *)(iVar5 + 0x20),0,0);
    FUN_00441386(*(undefined4 *)(iVar5 + 0x20),0,0);
    func_0x005b22bc(*(undefined4 *)(iVar5 + 0x20),0,0);
    FUN_0044e368(*(undefined4 *)(iVar5 + 0x20),0);
    FUN_0043ded4(*(undefined4 *)(iVar5 + 0x20),0x10);
    FUN_0043dfa4(*(undefined4 *)(iVar5 + 0x20),0x360);
    uVar6 = FUN_00499416(*(undefined4 *)(iVar5 + 0x20));
    FUN_0049942e(uVar6,0x5b3334);
    uVar7 = FUN_0044104c(0xffffff);
    FUN_0044140e(uVar6,uVar7,0);
    FUN_0043f4c0(uVar6,0x240,0x3fffffff);
    FUN_00499678(uVar6,0);
    FUN_0044145a(uVar6,1,0);
    FUN_0044143e(uVar6,*piVar2,0);
    FUN_0044144c(uVar6,0x1c - *(int *)(*piVar2 + 0xc),0);
    FUN_0043f6ac(uVar6,4);
    if (*(char *)(iVar5 + 0x8d) == '\0') {
      FUN_0043ded4(*(undefined4 *)(iVar5 + 0x20),1);
    }
    if (*(char *)(iVar5 + 0x8c) == '\0') {
      FUN_0043ded4(*(undefined4 *)(iVar5 + 100),1);
    }
    FUN_005b0d86();
    FUN_0058c238(*(undefined4 *)(iVar5 + 8),0xfa,0);
    uVar6 = 0;
  }
  else {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      uVar8 = 0x161;
      FUN_0043d574(2,PTR_s_conversate_ui_005b3528,PTR_s_D__01_workspace_s200_ap510b_iar__005b3524,
                   PTR_s_conversate_ui_action_display_mai_005b3520,0x161,
                   PTR_s_display_main_page_but_app_not_ru_005b351c,param_4);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__conversate_ui_display_main_page_005b352c);
    }
    uVar6 = 0xffffffff;
  }
  return CONCAT44(uVar8,uVar6);
}

