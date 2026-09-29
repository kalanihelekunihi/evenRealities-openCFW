
int _ring_policy_elapsed_ticks(int param_1)

{
  int iVar1;
  
  if (param_1 == 0) {
    iVar1 = -1;
  }
  else {
    iVar1 = _ring_policy_tick_now();
    iVar1 = iVar1 - param_1;
  }
  return iVar1;
}

