
undefined8 FUN_005d331e(int param_1,int param_2,int param_3,undefined4 param_4)

{
  uint uVar1;
  bool bVar2;
  
  FUN_0043c0e4(param_3,0x10,0);
  uVar1 = *(int *)(param_1 + 0x238) + param_2;
  bVar2 = uVar1 < *(uint *)(param_1 + 0x230);
  if (bVar2) {
    *(undefined4 *)(param_3 + 0xc) = *(undefined4 *)(*(int *)(param_1 + 0x240) + uVar1 * 4);
    *(undefined4 *)(param_3 + 4) = *(undefined4 *)(param_3 + 0xc);
    *(undefined4 *)(param_3 + 8) = *(undefined4 *)(*(int *)(param_1 + 0x240) + uVar1 * 4 + 4);
  }
  return CONCAT44(param_4,(uint)!bVar2);
}

