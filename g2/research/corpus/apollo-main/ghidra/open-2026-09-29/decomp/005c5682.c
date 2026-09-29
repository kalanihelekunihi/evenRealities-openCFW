
undefined8 FUN_005c5682(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  
  iVar1 = FUN_005c5722();
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    iVar3 = *(int *)(iVar1 + 0x18);
    iVar4 = FUN_005c45d8(iVar1,0);
    iVar4 = *(int *)(iVar4 + 0xc);
    iVar1 = FUN_005c45e2(iVar1,0);
    uVar2 = (iVar1 / 2 + (param_2 - iVar3)) / (iVar1 + iVar4);
    if (*(uint *)(param_1 + 0x3c) <= uVar2) {
      uVar2 = *(int *)(param_1 + 0x3c) - 1;
    }
  }
  return CONCAT44(param_4,uVar2);
}

