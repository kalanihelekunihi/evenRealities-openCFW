
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_0055225c(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 *puVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  short sVar7;
  byte bVar8;
  int iVar9;
  
  piVar1 = DAT_00552858;
  if (param_1 == 0) {
    iVar4 = FUN_0043d0ce();
    iVar9 = param_1;
    if (iVar4 << 0x1e < 0) {
      iVar9 = 0x87e;
      param_2 = DAT_00552868;
      FUN_0043d574(1,PTR_s_message_notify_list_ui_00552890,
                   PTR_s_D__01_workspace_s200_ap510b_iar__0055288c,
                   PTR_s_message_notify_page_init_00552888,0x87e,DAT_00552868,param_3,param_4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0055286c,DAT_0055286c);
    }
  }
  else {
    if (*DAT_00552858 == 0) {
      iVar9 = ui_common_api_fn_00509c1c();
      *piVar1 = iVar9;
      if (*piVar1 == 0) {
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          param_2 = DAT_0055285c;
          FUN_0043d574(1,PTR_s_message_notify_list_ui_00552890,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0055288c,
                       PTR_s_message_notify_page_init_00552888,0x886);
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_00552864,DAT_00552864);
        }
      }
    }
    *_DAT_00552894 = 0;
    puVar2 = DAT_00552870;
    FUN_0043c0e4(DAT_00552870,0x1d0,0);
    FUN_0054ff36();
    FUN_0043f506(param_1,0x240);
    FUN_0043f568(param_1,0x120);
    FUN_0043f0e0(param_1,0);
    FUN_0043f142(param_1,0);
    FUN_0043ded4(param_1,0x50000);
    FUN_0043dfa4(param_1,0xb014);
    FUN_0044e368(param_1,0);
    FUN_0044146a(param_1,0,0);
    uVar5 = FUN_0044104c(0);
    FUN_0044127e(param_1,uVar5,0);
    FUN_0044129e(param_1,0,0);
    FUN_0044131c(param_1,0,0);
    FUN_0054fa24(param_1,0,0);
    uVar5 = FUN_0043de82(param_1);
    *puVar2 = uVar5;
    FUN_0043f506(*puVar2,0x240);
    FUN_0043f568(*puVar2,0xd6);
    FUN_0043f6b8(*puVar2,1,0,0xfffffff0);
    FUN_0044131c(*puVar2,0,0);
    uVar5 = FUN_0044104c(0);
    FUN_0044127e(*puVar2,uVar5,0);
    FUN_0044129e(*puVar2,0xff,0);
    FUN_0044146a(*puVar2,0,0);
    FUN_0054fa24(*puVar2,0,0);
    FUN_0043dfa4(*puVar2,0x12);
    sVar7 = 8;
    cVar3 = FUN_0045a568();
    if (cVar3 == '\x01') {
      sVar7 = -8;
    }
    uVar5 = FUN_0043de82(*puVar2);
    puVar2[3] = uVar5;
    FUN_0043f506(puVar2[3],4);
    FUN_0043f568(puVar2[3],0x1c);
    FUN_0043f6b8(puVar2[3],7,sVar7 + 8,0x10);
    uVar5 = FUN_0044104c(0);
    FUN_0044127e(puVar2[3],uVar5,0);
    FUN_0044129e(puVar2[3],0xff,0);
    FUN_0044131c(puVar2[3],0,0);
    FUN_0044146a(puVar2[3],0,0);
    FUN_0054fa24(puVar2[3],0,0);
    FUN_0043ded4(puVar2[3],0x10);
    FUN_0044e368(puVar2[3],0);
    FUN_0044e3ca(puVar2[3],0xc);
    FUN_0043ded4(puVar2[3],1);
    for (bVar8 = 0; bVar8 < 10; bVar8 = bVar8 + 1) {
      uVar5 = FUN_0043de82(puVar2[3]);
      puVar2[bVar8 + 4] = uVar5;
      FUN_0043f506(puVar2[bVar8 + 4],4);
      FUN_0043f568(puVar2[bVar8 + 4],4);
      FUN_0043f6b8(puVar2[bVar8 + 4],0xd,0,(uint)bVar8 * 0xc);
      uVar5 = FUN_0044104c(_DAT_00552898);
      FUN_0044127e(puVar2[bVar8 + 4],uVar5,0);
      FUN_0044129e(puVar2[bVar8 + 4],0xff,0);
      FUN_0044131c(puVar2[bVar8 + 4],0,0);
      FUN_0044146a(puVar2[bVar8 + 4],0,0);
      FUN_0054fa24(puVar2[bVar8 + 4],0,0);
      FUN_0043dfa4(puVar2[bVar8 + 4],0x12);
    }
    uVar5 = FUN_0043de82(*puVar2);
    puVar2[0xe] = uVar5;
    FUN_0043f506(puVar2[0xe],4);
    FUN_0043f568(puVar2[0xe],4);
    iVar9 = 0;
    FUN_0043f6d6(puVar2[0xe],puVar2[3],1,0);
    uVar5 = FUN_0044104c(_DAT_00552898);
    FUN_0044127e(puVar2[0xe],uVar5,0);
    FUN_0044129e(puVar2[0xe],0xff,0);
    FUN_0044131c(puVar2[0xe],0,0);
    FUN_0044146a(puVar2[0xe],0,0);
    FUN_0054fa24(puVar2[0xe],0,0);
    FUN_0043dfa4(puVar2[0xe],0x12);
    FUN_0043ded4(puVar2[0xe],1);
    uVar5 = FUN_0043de82(*puVar2);
    puVar2[2] = uVar5;
    FUN_0043f506(puVar2[2],0x224);
    FUN_0043f568(puVar2[2],0xc6);
    FUN_0043f6b8(puVar2[2],2,sVar7 + 6,0x10);
    uVar5 = FUN_0044104c(0);
    FUN_0044127e(puVar2[2],uVar5,0);
    FUN_0044129e(puVar2[2],0xff,0);
    FUN_0044131c(puVar2[2],1,0);
    uVar5 = FUN_0044104c(0xffffff);
    FUN_004412ec(puVar2[2],uVar5,0);
    FUN_0044130c(puVar2[2],0xff,0);
    FUN_0044146a(puVar2[2],6,0);
    FUN_0054fa24(puVar2[2],0,0);
    FUN_0043dfa4(puVar2[2],0x12);
    uVar5 = FUN_00499416(puVar2[2]);
    puVar2[1] = uVar5;
    FUN_0043f506(puVar2[1],0x224);
    FUN_0043f568(puVar2[1],0x3fffffff);
    FUN_0043f6b8(puVar2[1],9,0,0);
    uVar5 = _DAT_0055289c;
    uVar6 = FUN_00460084(_DAT_0055289c);
    uVar5 = FUN_0045fffe(uVar5,uVar6);
    FUN_0049942e(puVar2[1],uVar5);
    FUN_0044145a(puVar2[1],2,0);
    uVar5 = FUN_0044104c(0xffffff);
    FUN_0044140e(puVar2[1],uVar5,0);
    FUN_0044143e(puVar2[1],*_DAT_005528a0,0);
    uVar5 = FUN_0044104c(0);
    FUN_0044127e(puVar2[1],uVar5,0);
    FUN_0044129e(puVar2[1],0xff,0);
    FUN_0044131c(puVar2[1],0,0);
    FUN_0054fa24(puVar2[1],0,0);
    FUN_0043dfa4(puVar2[1],0x12);
    uVar5 = FUN_0050fef8(*puVar2);
    puVar2[0xf] = uVar5;
    FUN_0043f506(puVar2[0xf],0x224);
    FUN_0043f568(puVar2[0xf],0xd6);
    FUN_0043f6b8(puVar2[0xf],9,sVar7 + 6,0);
    uVar5 = FUN_0044104c(0);
    FUN_0044127e(puVar2[0xf],uVar5,0);
    FUN_0044129e(puVar2[0xf],0xff,0);
    FUN_0054fa24(puVar2[0xf],0,0);
    FUN_0044146a(puVar2[0xf],0,0);
    uVar5 = FUN_0044104c(0);
    func_0x00441348(puVar2[0xf],uVar5,0);
    func_0x00441368(puVar2[0xf],0xff,0);
    FUN_0044133a(puVar2[0xf],0,0);
    FUN_00441378(puVar2[0xf],0,0);
    FUN_0043ded4(puVar2[0xf],0x10);
    FUN_0044e368(puVar2[0xf],0);
    FUN_0044e3ca(puVar2[0xf],0xc);
    for (bVar8 = 0; bVar8 < 3; bVar8 = bVar8 + 1) {
      iVar4 = FUN_00551814(puVar2[0xf],bVar8,puVar2 + (uint)bVar8 * 10 + 0x10);
      if (iVar4 == 0) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          iVar9 = 0x911;
          param_2 = _DAT_005528a4;
          FUN_0043d574(1,PTR_s_message_notify_list_ui_00552890,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0055288c,
                       PTR_s_message_notify_page_init_00552888,0x911,_DAT_005528a4,bVar8);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x4400000,_DAT_005528a8,_DAT_005528a8,bVar8);
        }
      }
      else {
        FUN_0043ded4(puVar2[(uint)bVar8 * 10 + 0x10],1);
      }
    }
    FUN_00551ed8(param_1,0);
  }
  return CONCAT44(param_2,iVar9);
}

