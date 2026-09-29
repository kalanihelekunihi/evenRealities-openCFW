
undefined4 FUN_005ecb88(short param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  iVar1 = DAT_005ed744;
  uVar2 = FUN_005eca48();
  if (*(int *)(iVar1 + 0x248) != 0) {
    FUN_005ecb08(*(undefined4 *)(iVar1 + 0x248),param_1 == -1);
  }
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1) {
    FUN_005ecb08(*(undefined4 *)(iVar1 + uVar3 * 4 + 0x24c),param_1 == (short)uVar3);
  }
  *(short *)(iVar1 + 0x27a) = param_1;
  return param_4;
}

