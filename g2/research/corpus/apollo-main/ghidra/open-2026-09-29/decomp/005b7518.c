
undefined4 FUN_005b7518(void)

{
  int iVar1;
  undefined4 in_r3;
  
  iVar1 = DAT_005b7604;
  FUN_0044d90e(*(undefined4 *)(DAT_005b7604 + 0x1c));
  *(undefined4 *)(iVar1 + 0x1c) = 0;
  *(undefined1 *)(iVar1 + 0x98) = 0;
  *(undefined4 *)(iVar1 + 0x24) = 0;
  *(undefined4 *)(iVar1 + 0x28) = 0;
  *(undefined4 *)(iVar1 + 0x2c) = 0;
  *(undefined2 *)(iVar1 + 0x60) = 0;
  FUN_0043c0e4(iVar1 + 0x30,0x30,0);
  FUN_0043dfa4(*(undefined4 *)(iVar1 + 0x7c),1);
  return in_r3;
}

