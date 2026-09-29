
undefined4 FUN_0058143a(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = FUN_0044a43c(param_1);
  iVar3 = 0;
  while( true ) {
    if (iVar1 <= iVar3) {
      return 1;
    }
    iVar2 = FUN_00595984(*(undefined1 *)(param_1 + iVar3));
    if (iVar2 == 0) break;
    iVar3 = iVar3 + 1;
  }
  return 0;
}

