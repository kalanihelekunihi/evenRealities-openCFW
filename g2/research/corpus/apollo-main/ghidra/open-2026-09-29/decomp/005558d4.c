
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_005558d4(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int *piVar2;
  undefined *puVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  uint uVar8;
  
  piVar2 = _DAT_00556260;
  pcVar1 = DAT_005560cc;
  *(undefined1 *)((int)_DAT_00556260 + 0x45) = 0;
  teleprompt_page_data_init
            (*(undefined4 *)(pcVar1 + 4),*(undefined4 *)(pcVar1 + 0xc),param_3,param_4,param_1,
             param_2,param_3,param_4);
  if (((param_1 & 0xff) == 1) && (*piVar2 != 0)) {
    FUN_0044d7b8(*piVar2);
    *piVar2 = 0;
  }
  iVar4 = func_0x005540f0();
  iVar5 = FUN_0043de82(piVar2[4]);
  piVar2[6] = iVar5;
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_teleprompt_ui_0055648c,PTR_s_D__01_workspace_s200_ap510b_iar__00556488,
                 PTR_s_teleprompt_ui_action_main_page_c_00556424,0x4f1,
                 PTR_s_display_width____d__display_line_00556420,*(undefined4 *)(pcVar1 + 0x14),
                 iVar4);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0x10800000,PTR_s__teleprompt_ui_display_width_____00556490,
                        PTR_s__teleprompt_ui_display_width_____00556490,
                        *(undefined4 *)(pcVar1 + 0x14),iVar4);
  }
  FUN_0043f4c0(piVar2[6],*(undefined4 *)(pcVar1 + 0x14),iVar4 * 0x1c);
  FUN_0043f6b8(piVar2[6],5,0xfffffffc,0);
  FUN_0044129e(piVar2[6],0,0);
  FUN_0044131c(piVar2[6],0,0);
  FUN_00554080(piVar2[6],0,0);
  FUN_0044146a(piVar2[6],0,0);
  FUN_0044e368(piVar2[6],0);
  FUN_0043ded4(piVar2[6],0x10);
  FUN_0044e3ca(piVar2[6],0xc);
  FUN_0043dfa4(piVar2[6],0x360);
  FUN_0048ba78(piVar2[6],1);
  FUN_0048ba92(piVar2[6],0,0,0);
  FUN_00441246(piVar2[6],0,0);
  for (uVar8 = 0; puVar3 = PTR_FUN_0055545c_1_0055649c, uVar8 < 4; uVar8 = uVar8 + 1) {
    iVar5 = FUN_00555486(piVar2[6]);
    if (iVar5 == 0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_teleprompt_ui_0055648c,PTR_s_D__01_workspace_s200_ap510b_iar__00556488,
                     PTR_s_teleprompt_ui_action_main_page_c_00556424,0x506,
                     PTR_s_Failed_to_pre_create_page_label_f_00556494,uVar8);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__teleprompt_ui_Failed_to_pre_cre_00556498,
                            PTR_s__teleprompt_ui_Failed_to_pre_cre_00556498,uVar8);
      }
    }
    else {
      FUN_0049942e(iVar5,0x555c00);
    }
  }
  FUN_00451740(piVar2[6],PTR_FUN_0055545c_1_0055649c,0xc,0);
  FUN_00451740(piVar2[6],puVar3,0xf,0);
  FUN_00451740(piVar2[6],puVar3,0xe,0);
  iVar5 = FUN_00554c68(piVar2[4]);
  piVar2[7] = iVar5;
  FUN_0043f6b8(piVar2[7],6,0,0);
  iVar5 = FUN_0043de82(piVar2[4]);
  piVar2[5] = iVar5;
  FUN_0043f4c0(piVar2[5],0x240,0x1c);
  uVar6 = func_0x005540f8(iVar4);
  FUN_0043f09a(piVar2[5],0,uVar6);
  FUN_0044129e(piVar2[5],0,0);
  FUN_0044131c(piVar2[5],0,0);
  FUN_00554080(piVar2[5],0,0);
  FUN_0044146a(piVar2[5],0,0);
  FUN_0043dfa4(piVar2[5],0x10);
  uVar6 = FUN_00499416(piVar2[5]);
  FUN_0043f4c0(uVar6,0x3fffffff,0x1c);
  FUN_0043f6b8(uVar6,8,0,0);
  puVar3 = PTR_s_ID_TELEPROMPT_ELAPSED_005564a0;
  uVar7 = FUN_00460084(PTR_s_ID_TELEPROMPT_ELAPSED_005564a0);
  uVar7 = FUN_0045fffe(puVar3,uVar7);
  FUN_0049954c(uVar6,PTR_s__s_0_00_00_005564a4,uVar7);
  FUN_0044143e(uVar6,*_DAT_00556128,0);
  uVar7 = FUN_0044104c(0xffffff);
  FUN_0044140e(uVar6,uVar7,0);
  FUN_0044145a(uVar6,3,0);
  uVar6 = 0;
  if (*pcVar1 == '\0') {
    uVar6 = FUN_0058c7a0(piVar2[5],PTR_FUN_00554e9c_1_0055665c);
  }
  else if (*pcVar1 == '\x01') {
    uVar6 = FUN_00499416(piVar2[5]);
    FUN_0044143e(uVar6,PTR_DAT_00556660,0);
    uVar7 = FUN_0044104c(0xffffff);
    FUN_0044140e(uVar6,uVar7,0);
    FUN_0044145a(uVar6,3,0);
    FUN_0049942e(uVar6,0x555cf0);
  }
  else if (*pcVar1 == '\x02') {
    uVar6 = FUN_00499416(piVar2[5]);
    FUN_0044143e(uVar6,PTR_DAT_00556660,0);
    uVar7 = FUN_0044104c(0xffffff);
    FUN_0044140e(uVar6,uVar7,0);
    FUN_0044145a(uVar6,3,0);
    FUN_0049942e(uVar6,0x555cf4);
  }
  FUN_0043f4c0(uVar6,0x3fffffff,0x3fffffff);
  FUN_0043f6b8(uVar6,7,0,0);
  FUN_0043ded4(piVar2[4],1);
  return 0;
}

