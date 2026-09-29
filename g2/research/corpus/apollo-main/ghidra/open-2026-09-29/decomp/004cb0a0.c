
void lfs_mlist_remove(int param_1,int param_2)

{
  int *piVar1;
  
  piVar1 = (int *)(param_1 + 0x28);
  while( true ) {
    if (*piVar1 == 0) {
      return;
    }
    if (*piVar1 == param_2) break;
    piVar1 = (int *)*piVar1;
  }
  *piVar1 = *(int *)*piVar1;
  return;
}

