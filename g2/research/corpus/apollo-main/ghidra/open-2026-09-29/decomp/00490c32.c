
undefined4 FUN_00490c32(undefined4 param_1)

{
  int iVar1;
  undefined1 auStack_30 [22];
  byte local_1a;
  
  iVar1 = FUN_004d94ba(auStack_30);
  do {
    if (iVar1 == 0) {
      return 1;
    }
    if ((local_1a & 0xf) == 10) {
      iVar1 = FUN_00490bf8(param_1,auStack_30);
      if (iVar1 == 0) {
        return 0;
      }
    }
    else {
      iVar1 = FUN_00490b1e(param_1,auStack_30);
      if (iVar1 == 0) {
        return 0;
      }
    }
    iVar1 = FUN_004d93d8(auStack_30);
  } while( true );
}

