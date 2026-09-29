
undefined8 FUN_004223d8(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  byte bVar3;
  
  if (param_1 < 0x39) {
    for (bVar3 = 0; bVar3 < 7; bVar3 = bVar3 + 1) {
      iVar2 = FUN_004215dc(bVar3,param_1);
      if (iVar2 != 0) {
        clock_release(bVar3,param_1);
      }
    }
    uVar1 = 0;
  }
  else {
    uVar1 = 6;
  }
  return CONCAT44(param_4,uVar1);
}

