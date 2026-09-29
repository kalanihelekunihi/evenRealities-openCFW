
undefined4 FUN_0050ac5c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  ushort uVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  int iVar9;
  undefined4 local_30 [4];
  undefined4 uStack_20;
  
  piVar1 = DAT_0050b160;
  uStack_20 = param_4;
  if (*DAT_0050b160 != 0) {
    ui_common_api_fn_00509c96(*DAT_0050b160);
    *piVar1 = 0;
  }
  if (*piVar1 == 0) {
    iVar5 = ui_common_api_fn_00509c1c();
    *piVar1 = iVar5;
    if (*piVar1 == 0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        local_30[1] = DAT_0050b430;
        local_30[0] = 0x2e6;
        FUN_0043d574(1,DAT_0050b5dc,DAT_0050b5d8,DAT_0050b434);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0050b5e0,DAT_0050b5e0);
      }
      return 0xffffffff;
    }
  }
  puVar2 = DAT_0050b5d4;
  osMutexAcquire(*DAT_0050b5d4,0xffffffff);
  uVar4 = FUN_0050b1ac();
  osMutexRelease(*puVar2);
  iVar5 = DAT_0050b14c;
  FUN_0043c0e4(DAT_0050b14c,0xcc,0);
  *(undefined4 *)(iVar5 + 200) = param_1;
  *(uint *)(iVar5 + 0xc0) = (uint)uVar4;
  *(undefined1 *)(iVar5 + 0xc4) = 0;
  iVar9 = DAT_0050b5e4;
  FUN_0043c0e4(DAT_0050b5e4,0x18,0);
  *(undefined1 *)(iVar9 + 0x14) = 0;
  FUN_00439c04(local_30,DAT_0050b5e8,0x10);
  for (iVar9 = 0; iVar9 < 4; iVar9 = iVar9 + 1) {
    FUN_0050b1bc(iVar9 * 0x30 + iVar5,param_1,local_30[iVar9]);
    *(undefined4 *)(iVar5 + iVar9 * 0x30 + 0x20) = local_30[iVar9];
  }
  if (uVar4 != 0) {
    for (iVar9 = 0; (iVar9 < 3 && (iVar9 < (int)(uint)uVar4)); iVar9 = iVar9 + 1) {
      FUN_0050b438(iVar5 + (iVar9 + 1) * 0x30,iVar9);
    }
  }
  FUN_0050c4ac(iVar5);
  for (iVar9 = 0; iVar9 < 4; iVar9 = iVar9 + 1) {
    FUN_0050b5f4(iVar9 * 0x30 + iVar5);
  }
  FUN_0044e368(*(undefined4 *)(iVar5 + 0x34),1);
  puVar2 = DAT_0050b5ec;
  uVar6 = FUN_0043de82(param_1);
  *puVar2 = uVar6;
  FUN_0043f4c0(*puVar2,DAT_0050b5f0,DAT_0050b5f0);
  FUN_0044129e(*puVar2,0xff,0);
  uVar6 = FUN_0044104c(0);
  FUN_0044127e(*puVar2,uVar6,0);
  FUN_0044131c(*puVar2,0,0);
  FUN_00509fdc(*puVar2,0,0);
  uVar6 = FUN_0043de82(*puVar2);
  FUN_0043f4c0(uVar6,0x3fffffff,0x3fffffff);
  FUN_0044129e(uVar6,0,0);
  FUN_0044131c(uVar6,0,0);
  FUN_00509fdc(uVar6,0,0);
  FUN_0048ba78(uVar6,0);
  FUN_0048ba92(uVar6,2,2,2);
  FUN_00441254(uVar6,8,0);
  FUN_0043f6b8(uVar6,2,0,0x74);
  uVar7 = FUN_00498668(uVar6);
  FUN_00498680(uVar7,DAT_0050b718);
  FUN_0043f506(uVar7,0x18);
  FUN_0043f568(uVar7,0x18);
  FUN_0043ded4(uVar7,0x10000);
  FUN_0043dfa4(uVar7,0x10);
  uVar7 = FUN_00499416(uVar6);
  uVar6 = DAT_0050b71c;
  uVar8 = FUN_00460084(DAT_0050b71c);
  uVar6 = FUN_0045fffe(uVar6,uVar8);
  FUN_0049942e(uVar7,uVar6);
  uVar6 = FUN_0044104c(0xffffff);
  FUN_0044140e(uVar7,uVar6,0);
  puVar3 = DAT_0050b720;
  FUN_0044143e(uVar7,*DAT_0050b720,0);
  uVar7 = FUN_00499416(*puVar2);
  uVar6 = DAT_0050b724;
  uVar8 = FUN_00460084(DAT_0050b724);
  uVar6 = FUN_0045fffe(uVar6,uVar8);
  FUN_0049942e(uVar7,uVar6);
  uVar6 = FUN_0044104c(0xffffff);
  FUN_0044140e(uVar7,uVar6,0);
  FUN_0044143e(uVar7,*puVar3,0);
  FUN_0044145a(uVar7,2,0);
  FUN_0043f6b8(uVar7,2,0,0x92);
  if (uVar4 == 0) {
    FUN_0043dfa4(*puVar2,1);
  }
  else {
    FUN_0043ded4(*puVar2,1);
  }
  *DAT_0050af9c = 0;
  *DAT_0050b044 = 1;
  return 0;
}

