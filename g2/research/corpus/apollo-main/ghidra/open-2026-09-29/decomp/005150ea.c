
void FUN_005150ea(int param_1,uint param_2)

{
  undefined4 uVar1;
  
  if (param_1 == 0) {
    uVar1 = 1;
  }
  else {
    if ((param_2 < 2) || ((param_2 == 2 || param_2 == 3) || param_2 == 4)) {
      *(char *)(param_1 + 0xd5) = (char)param_2;
      return;
    }
    uVar1 = 8;
  }
  FUN_0051565c(uVar1);
  return;
}

