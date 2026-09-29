
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_005555a4(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

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
  FUN_0044143e(uVar2,*_DAT_00556128,0);
  FUN_00441180(uVar2,500,0);
  FUN_004411aa(uVar2,0x1c,0);
  FUN_00499678(uVar2,1);
  FUN_0044145a(uVar2,1,0);
  uVar3 = FUN_0044104c(_DAT_005558bc);
  FUN_0044140e(uVar2,uVar3,0);
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    uVar5 = 0x488;
    FUN_0043d574(4,DAT_005558cc,DAT_005558c8,_DAT_00556130,0x488,_DAT_0055612c,param_3);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__teleprompt_ui_Button__s__create_0055641c,
                        PTR_s__teleprompt_ui_Button__s__create_0055641c,param_3);
  }
  return CONCAT44(uVar5,uVar1);
}

