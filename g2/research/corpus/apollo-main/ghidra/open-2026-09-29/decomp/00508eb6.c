
undefined4 FUN_00508eb6(int param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = (**(code **)(param_1 + 4))(param_2,param_4);
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    uVar2 = 0xfffffffd;
  }
  return uVar2;
}

