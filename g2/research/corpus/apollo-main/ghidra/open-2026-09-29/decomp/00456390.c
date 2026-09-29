
void FUN_00456390(short param_1,int param_2)

{
  if (param_1 < 0) {
    *(char *)(((int)param_1 & 0xfU) + DAT_00456568 + -4) = (char)(param_2 << 4);
  }
  else {
    *(char *)(DAT_00456564 + param_1) = (char)(param_2 << 4);
  }
  return;
}

