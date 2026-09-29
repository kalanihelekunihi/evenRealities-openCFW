
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0054787c(uint param_1)

{
  undefined *puVar1;
  undefined *puVar2;
  undefined *puVar3;
  undefined *puVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_navigation_ui_00548010,PTR_s_D__01_workspace_s200_ap510b_iar__0054800c,
                 PTR_s_navigation_ui_startup_failed_exi_005482ac,0x518,
                 PTR_s_navigation_ui_startup_failed_exi_005482a8);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_sta_005482b0,
                        PTR_s__navigation_ui_navigation_ui_sta_005482b0);
  }
  uVar6 = FUN_00499416(*_DAT_005482a0);
  FUN_0043f506(uVar6,0x3fffffff);
  FUN_0043f568(uVar6,0x3fffffff);
  FUN_0043f6ac(uVar6,9);
  puVar4 = PTR_s_ID_NAVIGATE_UNLOCK_YOUR_PHONE_TO_005482c0;
  puVar3 = PTR_s_ID_NAVIGATE_FAIL_NO_LOCATION_ACC_005482bc;
  puVar2 = PTR_s_ID_NAVIGATE_FAIL_SOMETHING_WENT__005482b8;
  puVar1 = PTR_s_ID_NAVIGATE_FAIL_LOCATION_TOO_FA_005482b4;
  if (param_1 == 1) {
    uVar7 = FUN_00460084(PTR_s_ID_NAVIGATE_FAIL_LOCATION_TOO_FA_005482b4);
    uVar7 = FUN_0045fffe(puVar1,uVar7);
    FUN_0049942e(uVar6,uVar7);
    goto LAB_00547988;
  }
  if (param_1 != 0) {
    if (param_1 == 3) {
      uVar7 = FUN_00460084(PTR_s_ID_NAVIGATE_FAIL_NO_LOCATION_ACC_005482bc);
      uVar7 = FUN_0045fffe(puVar3,uVar7);
      FUN_0049942e(uVar6,uVar7);
      goto LAB_00547988;
    }
    if (param_1 < 3) {
      uVar7 = FUN_00460084(PTR_s_ID_NAVIGATE_FAIL_SOMETHING_WENT__005482b8);
      uVar7 = FUN_0045fffe(puVar2,uVar7);
      FUN_0049942e(uVar6,uVar7);
      goto LAB_00547988;
    }
    if (param_1 == 4) {
      uVar7 = FUN_00460084(PTR_s_ID_NAVIGATE_UNLOCK_YOUR_PHONE_TO_005482c0);
      uVar7 = FUN_0045fffe(puVar4,uVar7);
      FUN_0049942e(uVar6,uVar7);
      goto LAB_00547988;
    }
  }
  uVar7 = FUN_00460084(PTR_s_ID_NAVIGATE_FAIL_LOCATION_TOO_FA_005482b4);
  uVar7 = FUN_0045fffe(puVar1,uVar7);
  FUN_0049942e(uVar6,uVar7);
LAB_00547988:
  FUN_0044143e(uVar6,*_DAT_0054854c,0);
  uVar7 = FUN_0044104c(0xffffff);
  FUN_0044140e(uVar6,uVar7,0);
  FUN_0044145a(uVar6,2,0);
  return;
}

