
undefined4 FUN_005322bc(int param_1)

{
  char cVar1;
  undefined4 unaff_r7;
  
  cVar1 = *(char *)(param_1 + 2);
  if (cVar1 == '\'') {
    FUN_005320c2();
  }
  else if (cVar1 == '(') {
    FUN_00532124();
  }
  else if (cVar1 == '*') {
    FUN_00532174();
  }
  else if (cVar1 == '+') {
    FUN_0053228e();
  }
  else if (cVar1 == ',') {
    FUN_0053223c();
  }
  return unaff_r7;
}

