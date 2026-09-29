
bool FUN_0045f706(int *param_1,int param_2)

{
  bool bVar1;
  
  if ((param_1 == (int *)0x0) || (param_2 == 0)) {
    bVar1 = false;
  }
  else if (*(char *)(param_2 + 0xb) == '\x01') {
    if (*param_1 == 0) {
      bVar1 = true;
    }
    else {
      bVar1 = *(byte *)(*param_1 + 0x16) <= *(byte *)(param_2 + 0x16);
    }
  }
  else {
    bVar1 = true;
  }
  return bVar1;
}

