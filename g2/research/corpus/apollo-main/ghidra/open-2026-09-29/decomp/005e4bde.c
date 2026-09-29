
undefined4 FUN_005e4bde(int param_1)

{
  undefined4 uVar1;
  
  if ((param_1 == 0) || (*(int *)(param_1 + 500) == 0)) {
    uVar1 = 0;
  }
  else if (*(char *)(param_1 + 0x278) == '\x02') {
    uVar1 = 0;
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

