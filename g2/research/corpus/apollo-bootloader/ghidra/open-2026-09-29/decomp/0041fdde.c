
void FUN_0041fdde(short param_1,int param_2)

{
  if (param_1 < 0) {
    *(char *)(((int)param_1 & 0xfU) + DAT_00420a00 + -4) = (char)(param_2 << 4);
  }
  else {
    *(char *)(DAT_00420870 + param_1) = (char)(param_2 << 4);
  }
  return;
}

