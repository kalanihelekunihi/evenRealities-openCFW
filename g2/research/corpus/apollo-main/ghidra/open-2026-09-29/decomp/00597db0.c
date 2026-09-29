
undefined4 FUN_00597db0(int param_1,int param_2,int param_3)

{
  undefined4 uVar1;
  int iVar2;
  
  if (*(uint *)(param_1 + 0x38) < (uint)(param_3 + param_2)) {
    uVar1 = 0xffffffff;
  }
  else {
    iVar2 = FUN_00597d10(param_1);
    if (iVar2 == 0) {
      uVar1 = 0xffffffff;
    }
    else {
      uVar1 = (**(code **)(iVar2 + 0x30))(param_2 + *(int *)(param_1 + 0x34),param_3);
    }
  }
  return uVar1;
}

