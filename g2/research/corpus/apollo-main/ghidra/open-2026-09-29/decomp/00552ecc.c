
int text_stream_common_prefix_length(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if ((param_1 == 0) || (param_2 == 0)) {
    iVar2 = 0;
  }
  else {
    iVar1 = FUN_0044a43c(param_1);
    iVar2 = FUN_0044a43c(param_2);
    if (iVar2 <= iVar1) {
      iVar1 = iVar2;
    }
    for (iVar3 = 0;
        (iVar2 = iVar1, iVar3 < iVar1 &&
        (iVar2 = iVar3, *(char *)(param_1 + iVar3) == *(char *)(param_2 + iVar3)));
        iVar3 = iVar3 + 1) {
    }
  }
  return iVar2;
}

