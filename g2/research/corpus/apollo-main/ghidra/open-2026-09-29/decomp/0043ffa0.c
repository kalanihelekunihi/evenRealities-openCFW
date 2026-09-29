
undefined8 FUN_0043ffa0(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar1 = FUN_0043eea6(param_1,0);
  iVar2 = FUN_0043eec4(param_1,0);
  if ((iVar1 == 0x3fffffff) || (iVar2 == 0x3fffffff)) {
    FUN_0043f648(param_1);
    uVar3 = 1;
  }
  else {
    uVar3 = 0;
  }
  return CONCAT44(param_4,uVar3);
}

