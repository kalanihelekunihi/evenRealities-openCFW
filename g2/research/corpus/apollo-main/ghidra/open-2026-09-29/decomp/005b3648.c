
bool FUN_005b3648(char param_1,char param_2,char param_3)

{
  bool bVar1;
  
  if (param_1 == '\a') {
    bVar1 = true;
  }
  else if (param_1 == '\b') {
    bVar1 = param_2 != param_3;
  }
  else {
    bVar1 = param_1 == param_2;
  }
  return bVar1;
}

