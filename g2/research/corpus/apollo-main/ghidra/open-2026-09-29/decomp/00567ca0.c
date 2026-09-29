
undefined8 FUN_00567ca0(undefined4 *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  
  uVar1 = 0;
  uVar2 = *param_1;
  if (*(int *)(param_2 + 0x48) == DAT_00567f70) {
    param_1[5] = *(undefined4 *)(param_2 + 100);
    param_1[6] = *(undefined4 *)(param_2 + 0x68);
    if ((int)((uint)*(byte *)(*(int *)(param_2 + 0x9c) + 4) << 0x1f) < 0) {
      FUN_00439c04(param_1 + 7,param_2 + 0x4c,0x18);
      *(uint *)(*(int *)(param_2 + 0x9c) + 4) = *(uint *)(*(int *)(param_2 + 0x9c) + 4) & 0xfffffffe
      ;
    }
    else {
      FUN_0058ed20(param_1 + 7);
      uVar1 = FUN_0058ed2e(uVar2,param_2 + 0x4c,param_1 + 7);
    }
  }
  else {
    uVar1 = 0x12;
  }
  return CONCAT44(param_4,uVar1);
}

