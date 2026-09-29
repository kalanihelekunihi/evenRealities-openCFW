
undefined1 FUN_004cc69e(int param_1,int param_2)

{
  undefined1 uVar1;
  uint uVar2;
  uint uVar3;
  
  if ((*(int *)(*(int *)(param_1 + 0x68) + 0x24) < 1) ||
     (uVar3 = *(int *)(param_2 + 8) + 1, uVar2 = *(int *)(*(int *)(param_1 + 0x68) + 0x24) + 1U | 1,
     uVar3 != uVar2 * (uVar3 / uVar2))) {
    uVar1 = 0;
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

