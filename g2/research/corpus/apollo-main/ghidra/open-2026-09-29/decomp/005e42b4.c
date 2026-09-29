
void FUN_005e42b4(void)

{
  int *piVar1;
  int *piVar2;
  
  piVar2 = (int *)((int)&DAT_005e42d8 + DAT_005e42d8);
  for (piVar1 = (int *)((int)&DAT_005e42d4 + DAT_005e42d4); piVar1 != piVar2;
      piVar1 = (int *)(*(code *)((int)piVar1 + *piVar1))(piVar1 + 1)) {
  }
  return;
}

