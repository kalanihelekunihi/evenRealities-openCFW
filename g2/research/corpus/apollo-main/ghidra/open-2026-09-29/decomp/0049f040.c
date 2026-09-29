
undefined4 _ring_policy_timeout_for_mode(char param_1)

{
  undefined4 uVar1;
  
  if (param_1 == '\x01') {
    uVar1 = 20000;
  }
  else if (param_1 == '\x02') {
    uVar1 = 3000;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

