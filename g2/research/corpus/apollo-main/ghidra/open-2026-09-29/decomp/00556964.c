
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_00556964(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined *puVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uStack_18;
  
  iVar1 = _DAT_00556cbc;
  iVar3 = FUN_0044dce2(*(undefined4 *)(_DAT_00556cbc + 0x14),2);
  uStack_18 = param_3;
  if (iVar3 == 0) {
    iVar3 = FUN_00498668(*(undefined4 *)(iVar1 + 0x14));
    FUN_00498680(iVar3,PTR_DAT_005573ec);
    uVar4 = FUN_0044104c(0);
    FUN_0044127e(iVar3,uVar4,0);
    FUN_0044129e(iVar3,0xff,0);
    FUN_004413ce(iVar3,0xff,0);
    FUN_0043f4c0(iVar3,0x3fffffff);
    FUN_0043f6b8(iVar3,7,0,0);
    uVar4 = FUN_00499416(*(undefined4 *)(iVar1 + 0x14));
    puVar2 = PTR_s_ID_GENERAL_PAUSE_005573f0;
    uVar5 = FUN_00460084(PTR_s_ID_GENERAL_PAUSE_005573f0);
    uVar5 = FUN_0045fffe(puVar2,uVar5);
    FUN_0049942e(uVar4,uVar5);
    FUN_0044143e(uVar4,*_DAT_005573f4,0);
    uVar5 = FUN_0044104c(0xffffff);
    FUN_0044140e(uVar4,uVar5,0);
    uStack_18 = 0;
    FUN_0043f6d6(uVar4,iVar3,0x14,8);
  }
  return CONCAT44(uStack_18,iVar3);
}

