
undefined8 FUN_005ea270(void)

{
  int iVar1;
  uint uVar2;
  undefined4 in_r3;
  
  iVar1 = DAT_005eadb4;
  if (*(int *)(DAT_005eadb4 + 0x1d4) == 0) {
    uVar2 = 0;
  }
  else {
    uVar2 = FUN_005ea256();
    uVar2 = uVar2 % 10;
    FUN_0049942e(*(undefined4 *)(iVar1 + 0x1d4),*(undefined4 *)(DAT_005eadb8 + uVar2 * 4));
  }
  return CONCAT44(in_r3,uVar2);
}

