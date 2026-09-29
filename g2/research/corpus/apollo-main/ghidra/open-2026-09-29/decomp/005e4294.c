
int * FUN_005e4294(void)

{
  int iVar1;
  int *piVar2;
  int *piVar3;
  int *piVar4;
  
  iVar1 = FUN_005e4228();
  if (iVar1 != 0) {
    FUN_005e42b4();
  }
  FUN_005ce01e(0);
  piVar2 = (int *)thunk_FUN_005e42e0();
  piVar4 = (int *)((int)&DAT_005e42d8 + DAT_005e42d8);
  piVar3 = (int *)((int)&DAT_005e42d4 + DAT_005e42d4);
  while (piVar3 != piVar4) {
    piVar2 = (int *)(*(code *)((int)piVar3 + *piVar3))(piVar3 + 1);
    piVar3 = piVar2;
  }
  return piVar2;
}

