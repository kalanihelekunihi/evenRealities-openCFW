
undefined4 lfs_mlist_isopen(int param_1,int param_2)

{
  int *piVar1;
  int local_4;
  
  piVar1 = &local_4;
  local_4 = param_1;
  while( true ) {
    if (*piVar1 == 0) {
      return 0;
    }
    if (*piVar1 == param_2) break;
    piVar1 = (int *)*piVar1;
  }
  return 1;
}

