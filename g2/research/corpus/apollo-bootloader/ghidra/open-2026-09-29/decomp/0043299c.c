
void init_array_run_43299c(void)

{
  int *piVar1;
  int *piVar2;
  
  piVar2 = (int *)((int)&DAT_004329c0 + DAT_004329c0);
  for (piVar1 = (int *)((int)&DAT_004329bc + DAT_004329bc); piVar1 != piVar2;
      piVar1 = (int *)(*(code *)((int)piVar1 + *piVar1))(piVar1 + 1)) {
  }
  return;
}

