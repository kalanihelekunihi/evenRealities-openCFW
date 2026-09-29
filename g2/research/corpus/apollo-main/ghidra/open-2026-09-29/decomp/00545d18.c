
int FUN_00545d18(undefined4 param_1,int param_2,short param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  undefined1 *puVar6;
  undefined4 *puVar7;
  int iVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  undefined4 local_3c;
  undefined4 local_38;
  undefined1 local_34;
  undefined1 local_33;
  undefined1 local_32;
  undefined1 local_31;
  undefined1 local_30;
  undefined1 local_2f;
  undefined4 uStack_28;
  
  uStack_28 = param_4;
  FUN_00585ca4();
  piVar1 = DAT_005467e0;
  if (*DAT_005467e0 != 0) {
    ui_common_api_fn_00509c96(*DAT_005467e0);
    *piVar1 = 0;
  }
  if (*piVar1 == 0) {
    iVar8 = ui_common_api_fn_00509c1c();
    *piVar1 = iVar8;
    if (*piVar1 == 0) {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(1,DAT_005467f0,DAT_005467ec,DAT_005467e8,0x217,DAT_005467e4);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_005467f4,DAT_005467f4);
      }
      return -1;
    }
  }
  *DAT_005467f8 = 0;
  *DAT_005467fc = 0;
  *DAT_00546800 = 0;
  *DAT_00546804 = 0;
  FUN_0043c0e4(DAT_00546808,0x50,0);
  *DAT_0054680c = 0;
  *DAT_00546810 = 0;
  *DAT_00546814 = 0;
  puVar2 = DAT_00546818;
  *DAT_00546818 = 0;
  puVar3 = DAT_0054681c;
  *DAT_0054681c = 0;
  uVar9 = DAT_00546820;
  FUN_0043c0e4(DAT_00546820,8,0);
  puVar4 = DAT_00546824;
  *DAT_00546824 = 0;
  puVar5 = DAT_00546828;
  *DAT_00546828 = 0;
  puVar6 = DAT_0054682c;
  *DAT_0054682c = 0;
  puVar7 = DAT_00546830;
  *DAT_00546830 = 0;
  *DAT_00546834 = 0;
  *DAT_00546838 = 0;
  *puVar6 = 0;
  *puVar2 = 0;
  *puVar3 = 0;
  FUN_0043c0e4(uVar9,8,0);
  *puVar4 = 0;
  *puVar5 = 0;
  *DAT_0054683c = 0;
  *DAT_00546840 = 0;
  FUN_0043c0e4(DAT_00546844,0x40,0);
  *DAT_00546848 = 0;
  *DAT_0054684c = 0;
  *DAT_00546850 = 0;
  *DAT_00546854 = 0;
  *DAT_00546858 = 0;
  *DAT_0054685c = 0;
  *DAT_00546860 = 0;
  puVar2 = DAT_00546864;
  osMutexAcquire(*DAT_00546864,0xffffffff);
  *DAT_00546868 = 0;
  FUN_0043c0e4(DAT_0054686c,0x55c,0);
  FUN_0043c0e4(DAT_00546870,0x18c,0);
  FUN_0043c0e4(DAT_00546874,0x4674,0);
  FUN_0043c0e4(DAT_00546878,0xea7c,0);
  FUN_0043c0e4(DAT_00546880,DAT_0054687c,0);
  osMutexRelease(*puVar2);
  *DAT_00546884 = 0;
  *DAT_00546888 = 0;
  *DAT_0054688c = 0;
  *DAT_00546890 = 0;
  *DAT_00546894 = 0;
  *DAT_00546898 = 0;
  *DAT_0054689c = 0;
  *DAT_005468a0 = 0;
  *puVar7 = 0;
  *DAT_005468a4 = 0;
  *DAT_005468a8 = 0;
  *DAT_005468ac = 0;
  piVar1 = DAT_005468b0;
  if (*DAT_005468b0 != 0) {
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      FUN_0043d574(2,DAT_005467f0,DAT_005467ec,DAT_005467e8,0x262,DAT_005468b4);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_005468b8,DAT_005468b8);
    }
    FUN_00463e1c(*piVar1,0);
  }
  *piVar1 = 0;
  puVar2 = DAT_005468bc;
  *DAT_005468bc = 0;
  puVar3 = DAT_005468c0;
  *DAT_005468c0 = 0;
  *DAT_005468c4 = 0;
  *DAT_005468c8 = 0x14;
  puVar4 = DAT_005468cc;
  uVar9 = FUN_0043de82(param_1);
  *puVar4 = uVar9;
  FUN_0043dfa4(*puVar4,0x10);
  FUN_0043f506(*puVar4,0x240);
  FUN_0043f568(*puVar4,0x120);
  FUN_0043f09a(*puVar4,0,0);
  FUN_0043dfa4(*puVar4,0x10);
  uVar9 = FUN_0044104c(0);
  FUN_0044127e(*puVar4,uVar9,0);
  FUN_0044129e(*puVar4,0xff,0);
  uVar9 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar4,uVar9,0);
  FUN_0044142e(*puVar4,0xff,0);
  uVar9 = FUN_0044104c(0);
  FUN_004412ec(*puVar4,uVar9,0);
  FUN_0044131c(*puVar4,0,0);
  FUN_0044133a(*puVar4,0,0);
  FUN_00441378(*puVar4,0,0);
  FUN_00441386(*puVar4,0,0);
  FUN_004413b0(*puVar4,0,0);
  FUN_00441394(*puVar4,0,0);
  FUN_004413a2(*puVar4,0,0);
  FUN_0044146a(*puVar4,0,0);
  FUN_00545594(*puVar4,0,0);
  FUN_0044120e(*puVar4,0,0);
  FUN_0044121c(*puVar4,0,0);
  FUN_0044122a(*puVar4,0,0);
  FUN_00441238(*puVar4,0,0);
  puVar5 = DAT_005468d0;
  uVar9 = FUN_0043de82(*puVar4);
  *puVar5 = uVar9;
  FUN_0043f506(*puVar5,0x240);
  FUN_0043f568(*puVar5,0x120);
  ui_common_api_fn_00509f7a(&local_38,&local_3c);
  FUN_0043f09a(*puVar5,local_38,local_3c);
  uVar9 = FUN_0044104c(0);
  FUN_0044127e(*puVar5,uVar9,0);
  FUN_0044129e(*puVar5,0,0);
  FUN_0044131c(*puVar5,0,0);
  FUN_0044133a(*puVar5,0,0);
  FUN_00441378(*puVar5,0,0);
  FUN_00441386(*puVar5,0,0);
  FUN_004413b0(*puVar5,0,0);
  FUN_00441394(*puVar5,0,0);
  FUN_004413a2(*puVar5,0,0);
  FUN_00545594(*puVar5,0,0);
  FUN_0044120e(*puVar5,0,0);
  FUN_0044121c(*puVar5,0,0);
  FUN_0044122a(*puVar5,0,0);
  FUN_00441238(*puVar5,0,0);
  FUN_0044146a(*puVar5,0,0);
  uVar9 = FUN_0044104c(0);
  FUN_004412ec(*puVar5,uVar9,0);
  uVar9 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar5,uVar9,0);
  FUN_0044142e(*puVar5,0xff,0);
  if (param_3 == 0) {
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005467f0,DAT_005467ec,DAT_005467e8,0x2a3,DAT_005468d4);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_005468d8,DAT_005468d8);
    }
    iVar8 = UX_GetSystemBLEStatus();
    if (iVar8 == 0) {
      uVar10 = FUN_00499416(*puVar5);
      FUN_0043f506(uVar10,0x3fffffff);
      FUN_0043f568(uVar10,0x3fffffff);
      FUN_0043f6ac(uVar10,9);
      uVar9 = DAT_005468dc;
      uVar11 = FUN_00460084(DAT_005468dc);
      uVar9 = FUN_0045fffe(uVar9,uVar11);
      FUN_0049942e(uVar10,uVar9);
      FUN_0044143e(uVar10,*DAT_005468e0,0);
      FUN_0044145a(uVar10,2,0);
      *puVar2 = 1;
      *puVar3 = 0xf0;
      iVar8 = 4;
      *DAT_005468e4 = 4;
    }
    else {
      uVar10 = FUN_00499416(*puVar5);
      FUN_0043f506(uVar10,0x3fffffff);
      FUN_0043f568(uVar10,0x3fffffff);
      FUN_0043f6ac(uVar10,9);
      uVar9 = DAT_005468e8;
      uVar11 = FUN_00460084(DAT_005468e8);
      uVar9 = FUN_0045fffe(uVar9,uVar11);
      FUN_0049942e(uVar10,uVar9);
      FUN_0044143e(uVar10,*DAT_005468e0,0);
      *DAT_005468e4 = 0;
      iVar8 = navigation_send_type_1_allocating();
    }
    return iVar8;
  }
  iVar8 = FUN_0043d0ce();
  if (iVar8 << 0x1e < 0) {
    FUN_0043d574(4,DAT_005467f0,DAT_005467ec,DAT_005467e8,699,DAT_005468ec);
  }
  iVar8 = FUN_0043d0ce();
  if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_005468f0,DAT_005468f0);
  }
  uVar10 = FUN_00499416(*puVar5);
  FUN_0043f506(uVar10,0x3fffffff);
  FUN_0043f568(uVar10,0x3fffffff);
  FUN_0043f6ac(uVar10,9);
  uVar9 = DAT_005468e8;
  uVar11 = FUN_00460084(DAT_005468e8);
  uVar9 = FUN_0045fffe(uVar9,uVar11);
  FUN_0049942e(uVar10,uVar9);
  FUN_0044143e(uVar10,*DAT_005468e0,0);
  *DAT_005468e4 = 1;
  navigation_send_type_5_shared(*(undefined1 *)(param_2 + 1),0);
  FUN_005455e4();
  iVar8 = FUN_0045a570();
  if (iVar8 != 1) {
    return iVar8;
  }
  iVar8 = semantic_get_flag_20074fdc();
  if (iVar8 != 0) {
    return iVar8;
  }
  navigation_send_type_16_allocating();
  FUN_0043c0e4(&local_34,10,0);
  local_34 = 0xf5;
  local_33 = 0;
  local_32 = 0;
  local_31 = 0;
  local_30 = 0;
  local_2f = 0;
  uVar9 = FUN_00464bb2(8,&local_34,6,0);
  iVar8 = FUN_0043d0ce();
  if (iVar8 << 0x1e < 0) {
    FUN_0043d574(4,DAT_005467f0,DAT_005467ec,DAT_005467e8,0x2d4,DAT_005468f4,uVar9);
  }
  iVar8 = FUN_0043d0ce();
  if (-1 < iVar8 << 0x1f) {
    iVar8 = FUN_0043d0ce();
    if (-1 < iVar8 << 0x1d) {
      return iVar8 << 0x1d;
    }
  }
  iVar8 = compress_log_output(0x10400000,DAT_005468f8,DAT_005468f8,uVar9);
  return iVar8;
}

