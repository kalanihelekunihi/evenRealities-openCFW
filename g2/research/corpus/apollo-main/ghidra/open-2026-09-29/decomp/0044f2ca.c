
void FUN_0044f2ca(undefined4 param_1)

{
  int iVar1;
  undefined1 auStack_28 [16];
  undefined1 auStack_18 [16];
  
  FUN_0044eb28(param_1,auStack_18,auStack_28);
  iVar1 = FUN_00450b80(auStack_18);
  if ((iVar1 != 0) || (iVar1 = FUN_00450b80(auStack_28), iVar1 != 0)) {
    iVar1 = FUN_00450b80(auStack_18);
    if (iVar1 != 0) {
      FUN_004405d4(param_1,auStack_18);
    }
    iVar1 = FUN_00450b80(auStack_28);
    if (iVar1 != 0) {
      FUN_004405d4(param_1,auStack_28);
    }
  }
  return;
}

