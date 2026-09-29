
undefined4 FUN_0048fdf2(int *param_1)

{
  int iVar1;
  undefined1 local_20;
  undefined1 auStack_1f [3];
  uint local_1c;
  undefined1 auStack_18 [16];
  
  FUN_0048949c(auStack_18,0x10);
  local_1c = 0;
  local_20 = 0;
  if (*(int *)(*param_1 + 8) != 0) {
    FUN_0048f49c(auStack_18,*(undefined4 *)(*param_1 + 8),0xffffffff);
    iVar1 = FUN_0048f66c(auStack_18,&local_20,&local_1c,auStack_1f);
    if (iVar1 == 0) {
      return 0;
    }
  }
  do {
    iVar1 = FUN_0048fce2(param_1);
    if (iVar1 == 0) {
      return 0;
    }
    if ((local_1c != 0) && (*(ushort *)(param_1 + 4) == local_1c)) {
      iVar1 = FUN_0048fbe4(auStack_18,local_20,param_1);
      if (iVar1 == 0) {
        return 0;
      }
      iVar1 = FUN_0048f66c(auStack_18,&local_20,&local_1c,auStack_1f);
      if (iVar1 == 0) {
        return 0;
      }
      if (param_1[8] != 0) {
        *(undefined1 *)param_1[8] = 0;
      }
    }
    iVar1 = FUN_004d93d8(param_1);
    if (iVar1 == 0) {
      return 1;
    }
  } while( true );
}

