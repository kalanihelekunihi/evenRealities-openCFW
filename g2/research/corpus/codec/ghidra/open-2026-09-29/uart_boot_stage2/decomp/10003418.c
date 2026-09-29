
undefined4 FUN_10003418(int param_1)

{
  undefined4 uVar1;
  
  if (*(uint *)(param_1 + 8) != 0) {
    uVar1 = (*(code *)(*(uint *)(param_1 + 8) & 0xfffffffe))();
    return uVar1;
  }
  return 0xffffffff;
}

