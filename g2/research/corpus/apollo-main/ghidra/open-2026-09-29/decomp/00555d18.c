
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_00555d18(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined *puVar2;
  ushort *puVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  int iVar7;
  
  piVar1 = _DAT_00556260;
  puVar3 = (ushort *)teleprompt_file_list_get();
  if (*piVar1 == 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_teleprompt_ui_0055648c,PTR_s_D__01_workspace_s200_ap510b_iar__00556488,
                   PTR_s_teleprompt_ui_action_file_list_u_00556674,0x57c,
                   PTR_s_Menu_page_is_NULL_00556670,param_3,param_4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__teleprompt_ui_Menu_page_is_NULL_00556678);
    }
    uVar5 = 0xffffffff;
  }
  else {
    FUN_0044d878(*piVar1);
    if (*puVar3 == 0) {
      uVar5 = FUN_00499416(*piVar1);
      puVar2 = PTR_s_ID_TELEPROMPT_NO_FILE_0055667c;
      uVar6 = FUN_00460084(PTR_s_ID_TELEPROMPT_NO_FILE_0055667c);
      uVar6 = FUN_0045fffe(puVar2,uVar6);
      FUN_0049942e(uVar5,uVar6);
      FUN_0043f4c0(uVar5,0x3fffffff,0x3fffffff);
      FUN_0043f6b8(uVar5,9,0,0);
      uVar6 = FUN_0044104c(0xffffff);
      FUN_0044140e(uVar5,uVar6,0);
      FUN_0044143e(uVar5,*_DAT_00556128,0);
      FUN_0044145a(uVar5,2,0);
      uVar5 = 0;
    }
    else {
      uVar5 = FUN_00499416(*piVar1);
      puVar2 = PTR_s_ID_TELEPROMPT_SELECT_00556680;
      uVar6 = FUN_00460084(PTR_s_ID_TELEPROMPT_SELECT_00556680);
      uVar6 = FUN_0045fffe(puVar2,uVar6);
      FUN_0049942e(uVar5,uVar6);
      FUN_0043f4c0(uVar5,0x3fffffff,0x28);
      FUN_0043f6b8(uVar5,1,0xc,0);
      uVar6 = FUN_0044104c(0xffffff);
      FUN_0044140e(uVar5,uVar6,0);
      FUN_0044143e(uVar5,*_DAT_00556128,0);
      FUN_0044145a(uVar5,2,0);
      iVar4 = FUN_0043de82(*piVar1);
      piVar1[1] = iVar4;
      FUN_0043f4c0(piVar1[1],_DAT_00556684,200);
      FUN_0043f6b8(piVar1[1],1,0,0x38);
      FUN_0048ba78(piVar1[1],1);
      FUN_0048ba92(piVar1[1],0,0,0);
      FUN_00441246(piVar1[1],0,0);
      FUN_0044122a(piVar1[1],0,0);
      FUN_00441238(piVar1[1],0,0);
      FUN_0044120e(piVar1[1],0,0);
      FUN_0044121c(piVar1[1],0,0);
      FUN_0044129e(piVar1[1],0,0);
      FUN_0044131c(piVar1[1],0,0);
      FUN_0044146a(piVar1[1],0,0);
      FUN_00441386(piVar1[1],0,0);
      FUN_0044e368(piVar1[1],0);
      FUN_0043ded4(piVar1[1],0x10);
      FUN_0043dfa4(piVar1[1],0x360);
      uVar5 = _DAT_00556960;
      FUN_00451740(piVar1[1],_DAT_00556960,0xc,0);
      FUN_00451740(piVar1[1],uVar5,0xe,0);
      func_0x00441498(piVar1[1],200,0);
      for (iVar4 = 0; iVar4 < (int)(uint)*puVar3; iVar4 = iVar4 + 1) {
        iVar7 = FUN_005555a4(piVar1[1],PTR_LAB_00556a18,puVar3 + iVar4 * 0x62 + 0x23);
        if (iVar7 == 0) {
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            FUN_0043d574(1,PTR_s_teleprompt_ui_0055648c,
                         PTR_s_D__01_workspace_s200_ap510b_iar__00556488,
                         PTR_s_teleprompt_ui_action_file_list_u_00556674,0x5b5,
                         PTR_s_Failed_to_create_button_for___s_00556a1c,puVar3 + iVar4 * 0x62 + 0x23
                        );
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            compress_log_output(0x4400000,PTR_s__teleprompt_ui_Failed_to_create_b_00556a20,
                                PTR_s__teleprompt_ui_Failed_to_create_b_00556a20,
                                puVar3 + iVar4 * 0x62 + 0x23);
          }
        }
        else if (iVar4 == 0) {
          piVar1[2] = iVar7;
          piVar1[3] = 0;
          FUN_005897ee(iVar7);
          FUN_0044130c(iVar7,0xff,0);
        }
      }
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_teleprompt_ui_0055648c,PTR_s_D__01_workspace_s200_ap510b_iar__00556488,
                     PTR_s_teleprompt_ui_action_file_list_u_00556674,0x5c2,
                     PTR_s_File_list_updated_with__d_items_00556a24,*puVar3);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__teleprompt_ui_File_list_updated_00556c34,
                            PTR_s__teleprompt_ui_File_list_updated_00556c34,*puVar3);
      }
      uVar5 = 0;
    }
  }
  return uVar5;
}

