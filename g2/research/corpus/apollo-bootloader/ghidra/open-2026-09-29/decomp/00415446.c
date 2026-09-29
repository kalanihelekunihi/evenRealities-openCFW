
undefined4 FUN_00415446(undefined4 *param_1)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = DAT_004155ec;
  iVar2 = FUN_004166aa(*DAT_004155ec,1000);
  if (iVar2 == 0) {
    iVar2 = FUN_00415180(*param_1,param_1 + 1);
    FUN_00416710(*puVar1);
    FUN_00415558(param_1);
    if (iVar2 < 0) {
      uVar3 = 0xffffffff;
    }
    else {
      uVar3 = 0;
    }
  }
  else {
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

