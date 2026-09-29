
undefined8 FUN_005d9296(int *param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  
  if (param_1[1] == 0) {
    iVar2 = *param_1;
    iVar3 = param_1[0xd];
    if ((param_3 == iVar3 + param_1[4]) &&
       ((uVar4 = param_2, param_3 = iVar2, uVar5 = param_4,
        iVar1 = FUN_005d8f7a(param_1 + 4,param_4,iVar3), iVar1 != 0 ||
        (iVar1 = FUN_005d8f7a(param_1 + 0xd,param_4,0,iVar3,param_2,iVar2,uVar5), uVar4 = param_2,
        param_3 = iVar2, iVar1 != 0)))) {
      param_1[1] = iVar1;
      param_2 = uVar4;
    }
  }
  return CONCAT44(param_3,param_2);
}

