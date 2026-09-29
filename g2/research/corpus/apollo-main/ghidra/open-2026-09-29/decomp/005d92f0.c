
undefined8 FUN_005d92f0(undefined4 *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  
  if (param_1[1] == 0) {
    uVar2 = *param_1;
    iVar3 = param_1[4];
    iVar4 = param_1[0xd];
    if (param_2 == iVar4 + iVar3) {
      param_2 = 0;
      uVar5 = uVar2;
      iVar1 = FUN_005d8f7a(param_1 + 4,param_3,0,iVar3,0,uVar2,param_4);
      if (iVar1 == 0) {
        param_2 = 0;
        iVar1 = FUN_005d8f7a(param_1 + 0xd,param_3,iVar3,iVar4,0,uVar2,param_4);
        uVar5 = uVar2;
        param_3 = uVar2;
        if (iVar1 == 0) goto LAB_005d932c;
      }
      param_1[1] = iVar1;
      param_3 = uVar5;
    }
  }
LAB_005d932c:
  return CONCAT44(param_3,param_2);
}

