
void remove_style(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = FUN_0044a43c(param_1);
  iVar2 = FUN_0044a43c(param_2);
  if (iVar2 < iVar1) {
    for (iVar3 = 1;
        (iVar3 <= iVar2 &&
        (*(char *)(param_1 + (iVar1 - iVar3)) == *(char *)(param_2 + (iVar2 - iVar3))));
        iVar3 = iVar3 + 1) {
    }
    if (iVar2 < iVar3) {
      iVar1 = iVar1 - iVar2;
      do {
        iVar1 = iVar1 + -1;
        if (iVar1 < 1) break;
      } while ((((*(char *)(param_1 + iVar1) == '-') || (*(char *)(param_1 + iVar1) == ' ')) ||
               (*(char *)(param_1 + iVar1) == '_')) || (*(char *)(param_1 + iVar1) == '+'));
      if (0 < iVar1) {
        *(undefined1 *)(param_1 + iVar1 + 1) = 0;
      }
    }
  }
  return;
}

