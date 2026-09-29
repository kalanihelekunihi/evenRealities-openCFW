
undefined4 semantic_terminal_state_allows_runtime_event(char param_1)

{
  undefined4 uVar1;
  
  if ((((param_1 == '\0') || (param_1 == '\x02')) || (param_1 == '\a')) ||
     ((param_1 == '\v' || (param_1 == '\f')))) {
    uVar1 = 1;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

