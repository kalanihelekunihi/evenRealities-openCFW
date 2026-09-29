
undefined8 FUN_004154d2(undefined4 *param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = DAT_004155ec;
  if (param_3 == 0) {
    uVar3 = 0;
  }
  else if (param_3 == 2) {
    uVar3 = 2;
  }
  else {
    if (1 < param_3) {
      uVar3 = 0xffffffff;
      goto LAB_0041552a;
    }
    uVar3 = 1;
  }
  iVar2 = FUN_004166aa(*DAT_004155ec,1000);
  if (iVar2 == 0) {
    iVar2 = FUN_00415232(*param_1,param_1 + 1,param_2,uVar3);
    FUN_00416710(*puVar1);
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
LAB_0041552a:
  return CONCAT44(param_4,uVar3);
}

