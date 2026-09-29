
void FUN_00460344(void)

{
  int iVar1;
  
  iVar1 = DAT_00460e04;
  *(undefined2 *)(DAT_00460e04 + 0x100) = 0;
  *(undefined2 *)(iVar1 + 0x102) = 0;
  *(undefined2 *)(iVar1 + 0x104) = 0;
  FUN_0043c0e4(iVar1,0x100,0);
  return;
}

