
undefined4 FUN_10003444(int param_1)

{
  undefined4 uVar1;
  
  if (*(uint *)(param_1 + 0x44) != 0) {
    uVar1 = (*(code *)(*(uint *)(param_1 + 0x44) & 0xfffffffe))();
    return uVar1;
  }
  return 0xffffffff;
}

