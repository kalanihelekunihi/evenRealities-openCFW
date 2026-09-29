
undefined8 FUN_005d4754(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_18;
  undefined4 local_14;
  
  FUN_005d4a94(param_1);
  *(undefined4 *)(param_1 + 0x2dd8) = param_2;
  *(undefined4 *)(param_1 + 0x2dc8) = param_2;
  *(undefined4 *)(param_1 + 0x2ddc) = param_3;
  *(undefined4 *)(param_1 + 0x2dcc) = param_3;
  *(undefined1 *)(param_1 + 0x2d93) = 1;
  iVar1 = FUN_005d36ea(param_1 + 8);
  if ((iVar1 == 0) ||
     (iVar1 = FUN_005d4b18(*(undefined4 *)(param_1 + 0x2d9c)), local_18 = param_3,
     local_14 = param_4, iVar1 != 0)) {
    local_14 = 0;
    local_18 = *(undefined4 *)(param_1 + 0x2da0);
    FUN_005d3c0a(param_1 + 8,*(undefined4 *)(param_1 + 0x2d94),*(undefined4 *)(param_1 + 0x2d98),
                 *(undefined4 *)(param_1 + 0x2d9c));
  }
  FUN_00439c04(param_1 + 0xf24,param_1 + 8,0xf1c);
  return CONCAT44(local_14,local_18);
}

