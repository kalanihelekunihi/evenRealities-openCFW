
undefined8 FUN_00452e68(undefined4 param_1,int param_2,int param_3,undefined4 param_4,char param_5)

{
  undefined4 uVar1;
  undefined4 uVar2;
  char cVar3;
  
  if (*(int *)(param_3 + 0x10) == 0) {
    uVar2 = FUN_0044c582();
  }
  else {
    uVar2 = *(undefined4 *)(*(int *)(param_3 + 0x10) + 0x39);
    if (param_2 != 0) {
      uVar2 = FUN_0044c54a(param_1,param_2,uVar2,*(int *)(param_3 + 0x10),uVar2,param_4);
    }
  }
  cVar3 = (char)((uint)uVar2 >> 0x18);
  if ((param_5 == '\0') || (cVar3 == '\0')) {
    if (cVar3 == '\0') {
      uVar2 = FUN_00440fde(param_4,param_5);
    }
  }
  else {
    uVar1 = FUN_00440fde(param_4,param_5);
    uVar2 = FUN_00482ef6(uVar2,uVar1);
  }
  return CONCAT44(uVar2,uVar2);
}

