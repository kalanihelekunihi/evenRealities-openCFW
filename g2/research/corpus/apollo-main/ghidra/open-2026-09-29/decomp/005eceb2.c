
undefined4 FUN_005eceb2(void)

{
  int iVar1;
  int iVar2;
  undefined4 in_r3;
  
  iVar1 = DAT_005ed9c4;
  if ((*(int *)(DAT_005ed9c4 + 0x240) != 0) &&
     (iVar2 = FUN_0043e2ea(*(undefined4 *)(DAT_005ed9c4 + 0x240)), iVar2 != 0)) {
    FUN_0044d7b8(*(undefined4 *)(iVar1 + 0x240));
  }
  *(undefined4 *)(iVar1 + 0x240) = 0;
  *(undefined4 *)(iVar1 + 0x244) = 0;
  FUN_0043c0e4(iVar1 + 0x248,0x2c,0);
  *(undefined1 *)(iVar1 + 0x27d) = 0;
  return in_r3;
}

