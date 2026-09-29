
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_005b1150(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  
  uVar5 = param_2;
  uVar2 = param_3;
  uVar1 = FUN_0043de82();
  FUN_0043f4c0(uVar1,0x3fffffff,0x28);
  FUN_0048ba78(uVar1,0);
  FUN_0048ba92(uVar1,0,2,2,uVar5,uVar2,param_4);
  FUN_0044146a(uVar1,6,0);
  FUN_00441254(uVar1,8,0);
  FUN_0044122a(uVar1,0xc,0);
  FUN_00441238(uVar1,0xc,0);
  FUN_0044131c(uVar1,1,0);
  FUN_0044130c(uVar1,0,0);
  FUN_0044129e(uVar1,0,0);
  FUN_0044132a(uVar1,0xf,0);
  uVar2 = FUN_0044104c(0xffffff);
  FUN_004412ec(uVar1,uVar2,0);
  FUN_0043dfa4(uVar1,0x10);
  uVar2 = FUN_00498668(uVar1);
  FUN_00498680(uVar2,param_2);
  uVar3 = FUN_0044104c(0);
  FUN_0044127e(uVar2,uVar3,0);
  FUN_0044129e(uVar2,0xff,0);
  FUN_004413ce(uVar2,0x33,0);
  uVar2 = FUN_00499416(uVar1);
  FUN_0049942e(uVar2,param_3);
  FUN_0044143e(uVar2,*_DAT_005b1a84,0);
  FUN_00441180(uVar2,0x186,0);
  FUN_004411aa(uVar2,0x1c,0);
  FUN_00499678(uVar2,1);
  FUN_0044145a(uVar2,1,0);
  uVar3 = FUN_0044104c(_DAT_005b1a88);
  FUN_0044140e(uVar2,uVar3,0);
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    uVar5 = 0x15b;
    FUN_0043d574(4,DAT_005b15d0,DAT_005b15cc,PTR_s_conversate_ui_button_create_005b1a90,0x15b,
                 PTR_s_Button__s__create_completed_005b1a8c,param_3);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__conversate_ui_Button__s__create_005b1a94,
                        PTR_s__conversate_ui_Button__s__create_005b1a94,param_3);
  }
  return CONCAT44(uVar5,uVar1);
}

