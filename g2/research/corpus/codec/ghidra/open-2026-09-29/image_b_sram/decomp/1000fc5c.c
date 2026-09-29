
undefined4 FUN_1000fc5c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  
  uVar1 = FUN_10010ca4();
  iVar2 = FUN_100121a0();
  if (0 < iVar2) {
    uVar6 = param_4;
    uVar3 = FUN_10011e50(param_3,param_4,0,0);
    iVar2 = FUN_100121a0(uVar1,param_2,uVar3,uVar6);
    if (0 < iVar2) {
      uVar1 = FUN_10011e14(uVar1,param_2,param_3,param_4);
    }
  }
  iVar2 = FUN_10012220(uVar1,param_2,0,0);
  if (iVar2 < 0) {
    uVar6 = param_2;
    uVar4 = FUN_1000fc58(uVar1,param_2);
    uVar3 = param_4;
    uVar5 = FUN_10011e50(param_3,param_4,0,0);
    iVar2 = FUN_100121a0(uVar4,uVar6,uVar5,uVar3);
    if (0 < iVar2) {
      uVar1 = FUN_10011de4(uVar1,param_2,param_3,param_4);
      return uVar1;
    }
  }
  return uVar1;
}

