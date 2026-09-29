
undefined4 FUN_0043f612(undefined4 param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_0043e11c(param_1,DAT_0043ff8c);
  if (iVar1 == 0) {
    iVar1 = FUN_0044dca2(param_1);
    if (iVar1 == 0) {
      uVar2 = 0;
    }
    else {
      iVar1 = FUN_0043efae(iVar1,0);
      if (iVar1 == 0) {
        uVar2 = 0;
      }
      else {
        uVar2 = 1;
      }
    }
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

