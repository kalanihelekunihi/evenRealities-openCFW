
int * runtime_start_43297c(void)

{
  int iVar1;
  int *piVar2;
  int *piVar3;
  int *piVar4;
  
  iVar1 = vector_table_relocate_432910();
  if (iVar1 != 0) {
    init_array_run_43299c();
  }
  FUN_0041b862(0);
  piVar2 = (int *)terminal_loop_4329c4();
  piVar4 = (int *)((int)&DAT_004329c0 + DAT_004329c0);
  piVar3 = (int *)((int)&DAT_004329bc + DAT_004329bc);
  while (piVar3 != piVar4) {
    piVar2 = (int *)(*(code *)((int)piVar3 + *piVar3))(piVar3 + 1);
    piVar3 = piVar2;
  }
  return piVar2;
}

