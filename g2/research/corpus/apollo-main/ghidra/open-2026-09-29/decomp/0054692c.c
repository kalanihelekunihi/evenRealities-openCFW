
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0054692c(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int *piVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  char *pcVar6;
  undefined4 *puVar7;
  int iVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  uint uVar11;
  undefined4 in_r3;
  undefined4 uStack_68;
  undefined4 uStack_64;
  undefined1 auStack_60 [16];
  undefined1 auStack_50 [24];
  uint uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_28;
  
  uStack_28 = in_r3;
  iVar8 = FUN_0043d0ce();
  if (iVar8 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_navigation_ui_00547790,PTR_s_D__01_workspace_s200_ap510b_iar__0054778c,
                 PTR_s_navigation_ui_create_map_page_00547788,0x36e,_DAT_005476d8);
  }
  iVar8 = FUN_0043d0ce();
  if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_cre_00547794,
                        PTR_s__navigation_ui_navigation_ui_cre_00547794);
  }
  piVar3 = _DAT_00547798;
  if (*_DAT_00547798 != 0) {
    FUN_0044d878(*_DAT_00547798);
  }
  puVar4 = _DAT_0054779c;
  uVar9 = FUN_0043de82(*piVar3);
  *puVar4 = uVar9;
  FUN_0043f4c0(*puVar4,0x240,0x120);
  ui_common_api_fn_00509f7a(&uStack_64,&uStack_68);
  FUN_0043f09a(*puVar4,uStack_64,uStack_68);
  FUN_0044129e(*puVar4,0,0);
  FUN_0044131c(*puVar4,0,0);
  FUN_0044133a(*puVar4,0,0);
  FUN_00441386(*puVar4,0,0);
  FUN_00545594(*puVar4,0,0);
  FUN_0044146a(*puVar4,0,0);
  FUN_0043dfa4(*puVar4,0x10);
  puVar1 = _DAT_005476dc;
  uVar9 = FUN_0043de82(*puVar4);
  *puVar1 = uVar9;
  FUN_0043f4c0(*puVar1,0x240,0x120);
  FUN_0043f09a(*puVar1,0,0);
  uVar9 = FUN_0044104c(0);
  FUN_0044127e(*puVar1,uVar9,0);
  FUN_0044129e(*puVar1,0xff,0);
  FUN_0044131c(*puVar1,0,0);
  FUN_0044133a(*puVar1,0,0);
  FUN_00441386(*puVar1,0,0);
  FUN_00545594(*puVar1,0,0);
  FUN_0044146a(*puVar1,0,0);
  FUN_0043dfa4(*puVar1,0x10);
  puVar2 = _DAT_005476e0;
  uVar9 = FUN_0043de82(*puVar4);
  *puVar2 = uVar9;
  FUN_0043f4c0(*puVar2,0x240,0x120);
  FUN_0043f09a(*puVar2,0,0);
  uVar9 = FUN_0044104c(0);
  FUN_0044127e(*puVar2,uVar9,0);
  FUN_0044129e(*puVar2,0xff,0);
  FUN_0044131c(*puVar2,0,0);
  FUN_0044133a(*puVar2,0,0);
  FUN_00441386(*puVar2,0,0);
  FUN_00545594(*puVar2,0,0);
  FUN_0044146a(*puVar2,0,0);
  FUN_0043dfa4(*puVar2,0x10);
  FUN_0043ded4(*puVar2,1);
  puVar5 = _DAT_005477a0;
  uVar9 = FUN_0043de82(*puVar4);
  *puVar5 = uVar9;
  FUN_0043f4c0(*puVar5,0x240,0x120);
  FUN_0043f09a(*puVar5,0,0);
  uVar9 = FUN_0044104c(0);
  FUN_0044127e(*puVar5,uVar9,0);
  FUN_0044129e(*puVar5,0xff,0);
  FUN_0044131c(*puVar5,0,0);
  FUN_0044133a(*puVar5,0,0);
  FUN_00441386(*puVar5,0,0);
  FUN_00545594(*puVar5,0,0);
  FUN_0044146a(*puVar5,0,0);
  FUN_0043dfa4(*puVar5,0x10);
  FUN_0043ded4(*puVar5,1);
  puVar4 = _DAT_005477a4;
  uVar9 = FUN_00499416(*puVar5);
  *puVar4 = uVar9;
  uVar9 = _DAT_005477a8;
  uVar10 = FUN_00460084(_DAT_005477a8);
  uVar9 = FUN_0045fffe(uVar9,uVar10);
  FUN_0049942e(*puVar4,uVar9);
  puVar5 = _DAT_00547868;
  FUN_0044143e(*puVar4,*_DAT_00547868,0);
  uVar9 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar4,uVar9,0);
  FUN_004409fa(*puVar4);
  FUN_0043ded4(*puVar4,0x10000);
  FUN_0043dfa4(*puVar4,0x10);
  puVar4 = _DAT_0054786c;
  uVar9 = FUN_00498668(*puVar1);
  *puVar4 = uVar9;
  pcVar6 = _DAT_00547870;
  if (*_DAT_00547870 == '\x01') {
    uVar9 = navigation_icon_name_for_code(*(undefined4 *)(_DAT_00547870 + 4));
    FUN_00498680(*puVar4,uVar9);
  }
  FUN_0043f506(*puVar4,0x3c);
  FUN_0043f568(*puVar4,0x3c);
  FUN_0043f0e0(*puVar4,0);
  FUN_0043f142(*puVar4,0xe4);
  FUN_0043ded4(*puVar4,0x10000);
  FUN_0043dfa4(*puVar4,0x10);
  puVar4 = _DAT_00547874;
  uVar9 = FUN_00499416(*puVar1);
  *puVar4 = uVar9;
  if (*pcVar6 == '\x01') {
    FUN_0049942e(*puVar4,pcVar6 + 8);
  }
  FUN_0044143e(*puVar4,*puVar5,0);
  uVar9 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar4,uVar9,0);
  FUN_0043f0e0(*puVar4,0x48);
  FUN_0043f142(*puVar4,0xe8);
  FUN_0043ded4(*puVar4,0x10000);
  FUN_0043dfa4(*puVar4,0x10);
  puVar4 = _DAT_00547878;
  uVar9 = FUN_00499416(*puVar1);
  *puVar4 = uVar9;
  if (*pcVar6 == '\x01') {
    FUN_0049942e(*puVar4,pcVar6 + 0x48);
  }
  FUN_0044143e(*puVar4,*puVar5,0);
  uVar9 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar4,uVar9,0);
  FUN_0043f506(*puVar4,0x170);
  FUN_0043f568(*puVar4,0x1e);
  FUN_0043f0e0(*puVar4,0x48);
  FUN_0043f142(*puVar4,0x104);
  FUN_0043ded4(*puVar4,0x10000);
  FUN_0043dfa4(*puVar4,0x10);
  uVar9 = service_time_current_epoch_get();
  service_time_epoch_to_calendar(uVar9,auStack_50);
  FUN_0043c0e4(auStack_60,0x10,0);
  *_DAT_005479b4 = uStack_38;
  *_DAT_005479b8 = uStack_34;
  iVar8 = FUN_0046650c();
  if (iVar8 == 1) {
    uVar11 = uStack_38 % 0xc;
    if (uVar11 == 0) {
      uVar11 = 0xc;
    }
    if (uStack_38 < 0xc) {
      uVar9 = 0x546d98;
    }
    else {
      uVar9 = 0x546d9c;
    }
    FUN_004b4728(auStack_60,_DAT_005479bc,uVar11,uStack_34,uVar9);
  }
  else {
    FUN_004b4728(auStack_60,_DAT_005479c0,uStack_38,uStack_34);
  }
  puVar4 = _DAT_005479c4;
  uVar9 = FUN_00499416(*puVar1);
  *puVar4 = uVar9;
  if (*pcVar6 == '\x01') {
    FUN_0049942e(*puVar4,auStack_60);
  }
  FUN_0044143e(*puVar4,*puVar5,0);
  uVar9 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar4,uVar9,0);
  FUN_0043f506(*puVar4,0x3fffffff);
  FUN_0043f568(*puVar4,0x3fffffff);
  FUN_0043f0e0(*puVar4,0);
  FUN_0043f142(*puVar4,0);
  FUN_0043ded4(*puVar4,0x10000);
  FUN_0043dfa4(*puVar4,0x10);
  FUN_0043f66c(*puVar4);
  iVar8 = FUN_0043fd9e(*puVar4);
  puVar4 = _DAT_00547a74;
  uVar9 = FUN_00498668(*puVar1);
  *puVar4 = uVar9;
  if (*(int *)(pcVar6 + 0x188) == 1) {
    FUN_00498680(*puVar4,_DAT_00547a78);
  }
  else {
    FUN_00498680(*puVar4,_DAT_00547a7c);
  }
  FUN_0043f506(*puVar4,0x18);
  FUN_0043f568(*puVar4,0x18);
  FUN_0043f0e0(*puVar4,iVar8 + 0x10);
  FUN_0043f142(*puVar4,2);
  FUN_0043ded4(*puVar4,0x10000);
  FUN_0043dfa4(*puVar4,0x10);
  puVar4 = _DAT_00547a80;
  uVar9 = FUN_00499416(*puVar1);
  *puVar4 = uVar9;
  if (*pcVar6 == '\x01') {
    FUN_0049942e(*puVar4,pcVar6 + 0x88);
  }
  FUN_0043f506(*puVar4,0x3fffffff);
  FUN_0043f568(*puVar4,0x1c);
  FUN_0044143e(*puVar4,*puVar5,0);
  uVar9 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar4,uVar9,0);
  FUN_0043f6b8(*puVar4,3,0,0);
  FUN_0043ded4(*puVar4,0x10000);
  FUN_0043dfa4(*puVar4,0x10);
  puVar7 = _DAT_00547a84;
  uVar9 = FUN_00499416(*puVar1);
  *puVar7 = uVar9;
  if (*pcVar6 == '\x01') {
    FUN_0049942e(*puVar7,pcVar6 + 200);
  }
  FUN_0044143e(*puVar7,*puVar5,0);
  uVar9 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar7,uVar9,0);
  FUN_0043f506(*puVar7,0x3fffffff);
  FUN_0043f568(*puVar7,0x1c);
  FUN_0043f6d6(*puVar7,*puVar4,0x11,0xfffffff0,0);
  FUN_0043ded4(*puVar7,0x10000);
  FUN_0043dfa4(*puVar7,0x10);
  uVar9 = FUN_0054e44c(*puVar1,0x78,0x78,0x1c8,0xa8);
  *_DAT_00547a88 = uVar9;
  puVar4 = _DAT_00547a8c;
  uVar9 = FUN_00498668(*puVar1);
  *puVar4 = uVar9;
  FUN_00498680(*puVar4,_DAT_00547a90);
  FUN_0043f506(*puVar4,0x14);
  FUN_0043f568(*puVar4,0x14);
  FUN_0043f0e0(*puVar4,0x1fa);
  FUN_0043f142(*puVar4,0xda);
  FUN_0043ded4(*puVar4,0x10000);
  FUN_0043dfa4(*puVar4,0x10);
  puVar4 = _DAT_00547a94;
  uVar9 = FUN_00498668(*puVar1);
  *puVar4 = uVar9;
  FUN_00498680(*puVar4,_DAT_00547a98);
  FUN_0043f506(*puVar4,6);
  FUN_0043f568(*puVar4,6);
  FUN_0043f0e0(*puVar4,0x1c8);
  FUN_0043f142(*puVar4,0xa8);
  FUN_0043ded4(*puVar4,0x10000);
  FUN_0043dfa4(*puVar4,0x10);
  puVar4 = _DAT_00547a9c;
  uVar9 = FUN_00498668(*puVar1);
  *puVar4 = uVar9;
  FUN_00498680(*puVar4,_DAT_00547aa0);
  FUN_0043f506(*puVar4,6);
  FUN_0043f568(*puVar4,6);
  FUN_0043f0e0(*puVar4,0x23a);
  FUN_0043f142(*puVar4,0xa8);
  FUN_0043ded4(*puVar4,0x10000);
  FUN_0043dfa4(*puVar4,0x10);
  puVar4 = _DAT_00547aa4;
  uVar9 = FUN_00498668(*puVar1);
  *puVar4 = uVar9;
  FUN_00498680(*puVar4,_DAT_00547aa8);
  FUN_0043f506(*puVar4,6);
  FUN_0043f568(*puVar4,6);
  FUN_0043f0e0(*puVar4,0x1c8);
  FUN_0043f142(*puVar4,0x11a);
  FUN_0043ded4(*puVar4,0x10000);
  FUN_0043dfa4(*puVar4,0x10);
  puVar4 = _DAT_00547aac;
  uVar9 = FUN_00498668(*puVar1);
  *puVar4 = uVar9;
  FUN_00498680(*puVar4,_DAT_00547ab0);
  FUN_0043f506(*puVar4,6);
  FUN_0043f568(*puVar4,6);
  FUN_0043f0e0(*puVar4,0x23a);
  FUN_0043f142(*puVar4,0x11a);
  FUN_0043ded4(*puVar4,0x10000);
  FUN_0043dfa4(*puVar4,0x10);
  puVar4 = _DAT_00547ab4;
  uVar9 = FUN_00499416(*puVar1);
  *puVar4 = uVar9;
  FUN_0043f506(*puVar4,0x78);
  FUN_0043f568(*puVar4,0x78);
  uVar9 = _DAT_00547ab8;
  uVar10 = FUN_00460084(_DAT_00547ab8);
  uVar9 = FUN_0045fffe(uVar9,uVar10);
  FUN_0049942e(*puVar4,uVar9);
  FUN_0044143e(*puVar4,*puVar5,0);
  uVar9 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar4,uVar9,0);
  FUN_0044129e(*puVar4,0xff,0);
  uVar9 = FUN_0044104c(0);
  FUN_0044127e(*puVar4,uVar9,0);
  FUN_0043f0e0(*puVar4,0x1c8);
  FUN_0043f142(*puVar4,0xa8);
  FUN_0043ded4(*puVar4,0x10000);
  if (pcVar6[0x18c] == '\x01') {
    FUN_0054e660(*_DAT_00547a88,_DAT_00547dc0,0xaa,0xaa,*_DAT_00547dbc * -10 + 0xe10,4);
    FUN_0043ded4(*puVar4,1);
  }
  else {
    FUN_0043dfa4(*puVar4,1);
  }
  puVar1 = _DAT_00547dc4;
  uVar9 = FUN_00499416(*puVar2);
  *puVar1 = uVar9;
  FUN_0049942e(*puVar1,auStack_60);
  FUN_0044143e(*puVar1,*puVar5,0);
  uVar9 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar1,uVar9,0);
  FUN_0043f506(*puVar1,0x3fffffff);
  FUN_0043f568(*puVar1,0x20);
  FUN_0043f0e0(*puVar1,0);
  FUN_0043f142(*puVar1,0);
  FUN_0043ded4(*puVar1,0x10000);
  FUN_0043dfa4(*puVar1,0x10);
  FUN_0043f66c(*puVar1);
  iVar8 = FUN_0043fd9e(*puVar1);
  puVar1 = _DAT_00547dc8;
  uVar9 = FUN_00498668(*puVar2);
  *puVar1 = uVar9;
  if (*(int *)(pcVar6 + 0x188) == 1) {
    FUN_00498680(*puVar1,_DAT_00547a78);
  }
  else {
    FUN_00498680(*puVar1,_DAT_00547a7c);
  }
  FUN_0043f506(*puVar1,0x18);
  FUN_0043f568(*puVar1,0x18);
  FUN_0043f0e0(*puVar1,iVar8 + 0x10);
  FUN_0043f142(*puVar1,2);
  FUN_0043ded4(*puVar1,0x10000);
  FUN_0043dfa4(*puVar1,0x10);
  puVar1 = _DAT_00547ebc;
  uVar9 = FUN_00499416(*puVar2);
  *puVar1 = uVar9;
  if (*pcVar6 == '\x01') {
    FUN_0049942e(*puVar1,pcVar6 + 0x88);
  }
  FUN_0044143e(*puVar1,*puVar5,0);
  uVar9 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar1,uVar9,0);
  FUN_0043f506(*puVar1,0x3fffffff);
  FUN_0043f568(*puVar1,0x20);
  FUN_0043f6b8(*puVar1,3,0,0);
  FUN_0043ded4(*puVar1,0x10000);
  FUN_0043dfa4(*puVar1,0x10);
  puVar4 = _DAT_00547ec0;
  uVar9 = FUN_00499416(*puVar2);
  *puVar4 = uVar9;
  if (*pcVar6 == '\x01') {
    FUN_0049942e(*puVar4,pcVar6 + 200);
  }
  FUN_0044143e(*puVar4,*puVar5,0);
  uVar9 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar4,uVar9,0);
  FUN_0043f506(*puVar4,0x3fffffff);
  FUN_0043f568(*puVar4,0x20);
  FUN_0043f6d6(*puVar4,*puVar1,0x11,0xfffffff0,0);
  FUN_0043ded4(*puVar4,0x10000);
  FUN_0043dfa4(*puVar4,0x10);
  puVar1 = _DAT_00547ec4;
  uVar9 = FUN_00499416(*puVar2);
  *puVar1 = uVar9;
  if (*pcVar6 == '\x01') {
    FUN_0049942e(*puVar1,pcVar6 + 0x148);
  }
  FUN_0044143e(*puVar1,*puVar5,0);
  uVar9 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar1,uVar9,0);
  FUN_0043f506(*puVar1,0x3fffffff);
  FUN_0043f568(*puVar1,0x20);
  if (*(int *)(pcVar6 + 0x188) == 1) {
    FUN_0043f09a(*puVar1,0xffffff9c,0xffffff9c);
    FUN_0043ded4(*puVar1,1);
  }
  else {
    FUN_0043f6d6(*puVar1,*puVar4,0x11,0xfffffff0,0);
    FUN_0043dfa4(*puVar1,1);
  }
  FUN_0043ded4(*puVar1,0x10000);
  FUN_0043dfa4(*puVar1,0x10);
  puVar7 = _DAT_00547fdc;
  uVar9 = FUN_00499416(*puVar2);
  *puVar7 = uVar9;
  if (*pcVar6 == '\x01') {
    FUN_0049942e(*puVar7,pcVar6 + 0x108);
  }
  FUN_0044143e(*puVar7,*puVar5,0);
  uVar9 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar7,uVar9,0);
  FUN_0043f506(*puVar7,0x3fffffff);
  FUN_0043f568(*puVar7,0x20);
  if (*(int *)(pcVar6 + 0x188) == 1) {
    FUN_0043f6d6(*puVar7,*puVar4,0x11,0xfffffff0,0);
  }
  else {
    FUN_0043f6d6(*puVar7,*puVar1,0x11,0xfffffff0,0);
  }
  FUN_0043ded4(*puVar7,0x10000);
  FUN_0043dfa4(*puVar7,0x10);
  puVar1 = _DAT_00547fe0;
  uVar9 = FUN_005456f6(*puVar2,0,0x20);
  *puVar1 = uVar9;
  puVar4 = _DAT_00547fe4;
  uVar9 = FUN_00499416(*puVar2);
  *puVar4 = uVar9;
  FUN_0044129e(*puVar4,0xff,0);
  uVar9 = FUN_0044104c(0);
  FUN_0044127e(*puVar4,uVar9,0);
  uVar9 = _DAT_00547fe8;
  uVar10 = FUN_00460084(_DAT_00547fe8);
  uVar9 = FUN_0045fffe(uVar9,uVar10);
  FUN_0049942e(*puVar4,uVar9);
  FUN_0044143e(*puVar4,*puVar5,0);
  uVar9 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar4,uVar9,0);
  FUN_0044145a(*puVar4,2,0);
  FUN_0043f506(*puVar4,0x240);
  FUN_0043f568(*puVar4,0xbc);
  FUN_0043f0e0(*puVar4,0);
  FUN_0043f142(*puVar4,0x20);
  FUN_0043ded4(*puVar4,0x10000);
  if (pcVar6[0x47ed] == '\x01') {
    FUN_0043ded4(*puVar4,1);
    FUN_005458a2(*puVar1,_DAT_00547fec);
  }
  else {
    FUN_0043dfa4(*puVar4,1);
  }
  iVar8 = FUN_0043d0ce();
  if (iVar8 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_navigation_ui_00547790,PTR_s_D__01_workspace_s200_ap510b_iar__0054778c,
                 PTR_s_navigation_ui_create_map_page_00547788,0x4f5,
                 PTR_s_Navigation_multi_layer_container_00547ff0);
  }
  iVar8 = FUN_0043d0ce();
  if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
    compress_log_output(0x10000000,_DAT_00548298,_DAT_00548298);
  }
  return 0;
}

