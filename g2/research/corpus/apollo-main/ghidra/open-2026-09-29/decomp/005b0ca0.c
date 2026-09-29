
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_005b0ca0(int param_1,undefined1 param_2,undefined1 param_3,int param_4,undefined4 param_5)

{
  int iVar1;
  int iStack_80;
  undefined4 uStack_7c;
  undefined *puStack_60;
  undefined4 uStack_50;
  int iStack_4c;
  int iStack_20;
  
  if ((param_1 != 0) &&
     (iStack_20 = param_4, iVar1 = FUN_0043e2ea(param_1), uStack_7c = _DAT_005b1720, iVar1 != 0)) {
    FUN_00450500(param_1,_DAT_005b1720);
    FUN_00441488(param_1,param_2,0);
    FUN_004503d6(&iStack_80);
    iStack_80 = param_1;
    FUN_004506ce(&iStack_80,param_2,param_3);
    iStack_4c = -param_4;
    uStack_50 = param_5;
    puStack_60 = PTR_LAB_00450688_1_005b198c;
    FUN_00450408(&iStack_80);
  }
  return;
}

