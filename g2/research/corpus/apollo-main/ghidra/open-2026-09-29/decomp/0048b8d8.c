
undefined8 FUN_0048b8d8(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  
  uVar1 = *(uint *)(param_1 + 4);
  FUN_00450b5c(param_2,0,0,(*(uint *)(param_1 + 4) & 0xffff) - 1);
  return CONCAT44(param_4,(uVar1 >> 0x10) - 1);
}

