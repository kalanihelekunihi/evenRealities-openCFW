
void FUN_0043e63e(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  undefined1 auStack_a0 [16];
  undefined1 auStack_90 [16];
  undefined1 auStack_80 [8];
  undefined4 local_78;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  FUN_0044eb28(param_1,auStack_90,auStack_a0);
  iVar2 = FUN_00450b80(auStack_90);
  if (((iVar2 != 0) || (iVar2 = FUN_00450b80(auStack_a0), iVar2 != 0)) &&
     (cVar1 = FUN_0043e6a6(param_1,auStack_80), cVar1 == '\x01')) {
    iVar2 = FUN_00450b80(auStack_90);
    if (iVar2 != 0) {
      local_78 = 0;
      FUN_00451c6e(param_2,auStack_80,auStack_90);
    }
    iVar2 = FUN_00450b80(auStack_a0);
    if (iVar2 != 0) {
      local_78 = 1;
      FUN_00451c6e(param_2,auStack_80,auStack_a0);
    }
  }
  return;
}

