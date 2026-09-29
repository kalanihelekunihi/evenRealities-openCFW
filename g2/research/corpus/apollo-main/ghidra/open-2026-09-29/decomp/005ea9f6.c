
undefined4 FUN_005ea9f6(void)

{
  int iVar1;
  undefined4 in_r3;
  
  iVar1 = DAT_005eb28c;
  FUN_0043c0e4(DAT_005eb28c + 0x3c,0x80,0);
  FUN_0043c0e4(iVar1 + 0xbc,0x104,0);
  *(undefined4 *)(iVar1 + 0x1c8) = 0;
  *(undefined2 *)(iVar1 + 0x1c4) = 0;
  if (*(int *)(iVar1 + 8) != 0) {
    FUN_0043f4c0(*(undefined4 *)(iVar1 + 8),0x240,0);
  }
  FUN_005ea7dc();
  if (*(int *)(iVar1 + 4) != 0) {
    FUN_0044ea04(*(undefined4 *)(iVar1 + 4),0,0);
  }
  *(undefined1 *)(iVar1 + 0x28c) = 1;
  return in_r3;
}

