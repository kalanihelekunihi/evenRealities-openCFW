
undefined4 FUN_00418a98(void)

{
  int *piVar1;
  undefined4 in_r3;
  int iVar2;
  
  while( true ) {
    piVar1 = DAT_0041921c;
    if (*DAT_0041921c == 0) break;
    FUN_0041b3e4();
    iVar2 = *(int *)(*(int *)(DAT_00419210 + 0xc) + 0xc);
    FUN_0041b5a8(iVar2 + 4);
    *DAT_00419204 = *DAT_00419204 + -1;
    *piVar1 = *piVar1 + -1;
    FUN_0041b3fc();
    FUN_00418ae8(iVar2);
  }
  return in_r3;
}

