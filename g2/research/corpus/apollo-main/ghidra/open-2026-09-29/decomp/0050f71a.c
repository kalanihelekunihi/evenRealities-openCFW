
undefined4 FUN_0050f71a(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 local_1c [2];
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  iVar1 = FUN_0050f710(param_1);
  if (iVar1 == 0) {
    local_1c[0] = 0;
  }
  else {
    uVar2 = FUN_0050e9cc(param_1,0x40000);
    uVar3 = FUN_0050e9d6(param_1,0x40000);
    uVar4 = FUN_004997f8(iVar1);
    FUN_00489546(local_1c,uVar4,uVar2,uVar3,0,0x1fffffff,0);
  }
  return local_1c[0];
}

