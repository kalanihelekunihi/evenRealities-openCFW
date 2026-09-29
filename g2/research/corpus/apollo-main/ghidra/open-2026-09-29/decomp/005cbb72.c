
undefined8 FUN_005cbb72(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  if ((*(byte *)(param_1 + 0x70) & 0x3f) >> 3 == 0) {
    iVar1 = FUN_0043fd9e(param_1);
    iVar2 = FUN_0043fdda(param_1);
    uVar3 = (uint)(iVar2 <= iVar1);
  }
  else if ((*(byte *)(param_1 + 0x70) & 0x3f) >> 3 == 1) {
    uVar3 = 1;
  }
  else {
    uVar3 = 0;
  }
  return CONCAT44(param_4,uVar3);
}

