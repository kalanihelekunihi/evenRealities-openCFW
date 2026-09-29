
int text_stream_is_complete(int param_1)

{
  int iVar1;
  
  if (param_1 == 0) {
    iVar1 = 0;
  }
  else if ((*(int *)(param_1 + 4) == 0) || (*(int *)(param_1 + 0x10) == 0)) {
    iVar1 = *(int *)(param_1 + 8);
  }
  else {
    iVar1 = *(int *)(param_1 + 0x10) - *(int *)(param_1 + 0xc);
    if (iVar1 < 1) {
      iVar1 = *(int *)(param_1 + 8);
    }
    else if (*(char *)(param_1 + 0x2c) == '\0') {
      iVar1 = *(int *)(param_1 + 8) * (iVar1 + 1);
    }
    else {
      iVar1 = *(int *)(param_1 + 8) * iVar1;
    }
  }
  return iVar1;
}

