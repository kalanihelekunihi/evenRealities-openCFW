
undefined4 FUN_004556e0(void)

{
  int *piVar1;
  undefined4 in_r3;
  int iVar2;
  
  while( true ) {
    piVar1 = DAT_00456058;
    if (*DAT_00456058 == 0) break;
    FUN_004420d0();
    iVar2 = *(int *)(*(int *)(DAT_0045604c + 0xc) + 0xc);
    uxListRemove(iVar2 + 4);
    *DAT_00456040 = *DAT_00456040 + -1;
    *piVar1 = *piVar1 + -1;
    FUN_004420e8();
    FUN_00455836(iVar2);
  }
  return in_r3;
}

