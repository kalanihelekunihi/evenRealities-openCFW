
void FUN_005d4b4c(int param_1,undefined4 param_2,undefined4 param_3)

{
  undefined1 uVar1;
  int iVar2;
  uint uVar3;
  
  iVar2 = FUN_005d4b24(param_1,param_3);
  if (iVar2 != 0) {
    for (uVar3 = 0; uVar3 < *(uint *)(param_1 + 0xc); uVar3 = uVar3 + 1) {
      uVar1 = FUN_005d6d98(param_2);
      *(undefined1 *)(param_1 + uVar3 + 0x10) = uVar1;
    }
  }
  return;
}

