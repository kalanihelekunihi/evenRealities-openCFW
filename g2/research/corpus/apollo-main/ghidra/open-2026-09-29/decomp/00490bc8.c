
undefined4 FUN_00490bc8(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_30 [40];
  
  iVar1 = FUN_004d94d2(auStack_30);
  if (iVar1 == 0) {
    uVar2 = DAT_004910cc;
    if (*(int *)(param_1 + 0x10) != 0) {
      uVar2 = *(undefined4 *)(param_1 + 0x10);
    }
    *(undefined4 *)(param_1 + 0x10) = uVar2;
    uVar2 = 0;
  }
  else {
    uVar2 = FUN_00490b1e(param_1,auStack_30);
  }
  return uVar2;
}

