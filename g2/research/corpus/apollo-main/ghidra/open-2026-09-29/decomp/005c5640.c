
undefined8 FUN_005c5640(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uStack_20;
  undefined4 local_1c;
  undefined4 uStack_18;
  
  iVar4 = *(int *)(param_1 + 0x2c);
  uStack_20 = param_2;
  local_1c = param_3;
  uStack_18 = param_4;
  iVar1 = FUN_00452ef8();
  if ((iVar1 != 0) &&
     ((iVar2 = FUN_00452f00(iVar1), iVar2 == 1 || (iVar2 = FUN_00452f00(iVar1), iVar2 == 3)))) {
    FUN_00452f5e(iVar1,&uStack_20);
    uVar3 = FUN_005c5682(iVar4,local_1c);
    *(undefined4 *)(iVar4 + 0x48) = uVar3;
    FUN_00440656(param_1);
  }
  return CONCAT44(local_1c,uStack_20);
}

