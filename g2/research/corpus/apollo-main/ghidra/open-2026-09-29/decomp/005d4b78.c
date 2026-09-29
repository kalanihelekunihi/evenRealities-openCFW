
undefined4 FUN_005d4b78(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = FUN_005d4b24(param_1);
  if (iVar1 != 0) {
    for (uVar2 = 0; uVar2 < *(uint *)(param_1 + 0xc); uVar2 = uVar2 + 1) {
      *(undefined1 *)(param_1 + uVar2 + 0x10) = 0xff;
    }
    *(byte *)(*(int *)(param_1 + 0xc) + param_1 + 0xf) =
         *(byte *)(*(int *)(param_1 + 0xc) + param_1 + 0xf) & ~((char)(1 << (-param_2 & 7U)) - 1U);
  }
  return param_4;
}

