
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_005477ac(void)

{
  int *piVar1;
  undefined *puVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 in_r3;
  
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_navigation_ui_00548010,PTR_s_D__01_workspace_s200_ap510b_iar__0054800c,
                 PTR_s_navigation_ui_create_none_locati_00548008,0x507,
                 PTR_s_navigation_ui_create_none_locati_00548004,in_r3);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10000000,_DAT_0054829c,_DAT_0054829c);
  }
  piVar1 = _DAT_005482a0;
  if (*_DAT_005482a0 != 0) {
    FUN_0044d878(*_DAT_005482a0);
  }
  uVar4 = FUN_00499416(*piVar1);
  FUN_0043f506(uVar4,0x3fffffff);
  FUN_0043f568(uVar4,0x3fffffff);
  FUN_004409fa(uVar4);
  puVar2 = PTR_s_ID_NAVIGATE_NO_FAVORITE_LOCATION_005482a4;
  uVar5 = FUN_00460084(PTR_s_ID_NAVIGATE_NO_FAVORITE_LOCATION_005482a4);
  uVar5 = FUN_0045fffe(puVar2,uVar5);
  FUN_0049942e(uVar4,uVar5);
  FUN_0044143e(uVar4,*_DAT_00547868,0);
  uVar5 = FUN_0044104c(0xffffff);
  FUN_0044140e(uVar4,uVar5,0);
  FUN_0044145a(uVar4,2,0);
  return;
}

