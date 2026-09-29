
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_00546620(void)

{
  int *piVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined *puVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uStack_40;
  undefined *puStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined1 auStack_30 [24];
  undefined1 auStack_18 [4];
  undefined1 auStack_14 [4];
  
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    puStack_3c = PTR_s_navigation_ui_create_calibrate_c_00546908;
    uStack_40 = 0x31c;
    FUN_0043d574(4,DAT_005467f0,DAT_005467ec,PTR_s_navigation_ui_create_calibrate_c_0054690c);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_cre_00546910,
                        PTR_s__navigation_ui_navigation_ui_cre_00546910);
  }
  piVar1 = DAT_005468cc;
  if (*DAT_005468cc != 0) {
    FUN_0044d878(*DAT_005468cc);
  }
  puVar2 = _DAT_00546914;
  uVar6 = FUN_0043de82(*piVar1);
  *puVar2 = uVar6;
  FUN_0043f4c0(*puVar2,0x240,0x120);
  ui_common_api_fn_00509f7a(&uStack_34,&uStack_38);
  FUN_0043f09a(*puVar2,uStack_34,uStack_38);
  FUN_0044129e(*puVar2,0,0);
  FUN_0044131c(*puVar2,0,0);
  FUN_0044133a(*puVar2,0,0);
  FUN_00441386(*puVar2,0,0);
  FUN_00545594(*puVar2,0,0);
  FUN_0044146a(*puVar2,0,0);
  FUN_0043dfa4(*puVar2,0x10);
  puVar3 = _DAT_00546918;
  uVar6 = FUN_00499416(*puVar2);
  *puVar3 = uVar6;
  FUN_0043f506(*puVar3,0x3fffffff);
  FUN_0043f568(*puVar3,0x3fffffff);
  puVar4 = PTR_s_ID_NAVIGATE_CALIBRATE_COMPASS_0054691c;
  uVar6 = FUN_00460084(PTR_s_ID_NAVIGATE_CALIBRATE_COMPASS_0054691c);
  uVar6 = FUN_0045fffe(puVar4,uVar6);
  FUN_0049942e(*puVar3,uVar6);
  FUN_0044143e(*puVar3,*DAT_005468e0,0);
  FUN_0044145a(*puVar3,2,0);
  uVar6 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar3,uVar6,0);
  FUN_0043f6b8(*puVar3,2,0,0x95);
  FUN_00439c04(auStack_30,PTR_DAT_00546920,0x20);
  uStack_40 = FUN_00441094();
  FUN_00439be4(auStack_18,&uStack_40,3);
  uStack_40 = FUN_004410a6();
  FUN_00439be4(auStack_14,&uStack_40,3);
  piVar1 = DAT_005468b0;
  iVar5 = FUN_00463c68(*puVar2,auStack_30);
  *piVar1 = iVar5;
  if (*piVar1 == 0) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      puStack_3c = PTR_s_Failed_to_create_loading_animati_00546924;
      uStack_40 = 0x362;
      FUN_0043d574(1,DAT_005467f0,DAT_005467ec,PTR_s_navigation_ui_create_calibrate_c_0054690c);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__navigation_ui_Failed_to_create_l_00546928);
    }
  }
  else {
    FUN_0043f09a(*(undefined4 *)*piVar1,0x110,0x6d);
    FUN_00463ea6(*piVar1);
  }
  return 0;
}

