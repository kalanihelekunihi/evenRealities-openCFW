
void FUN_00584a10(short param_1,int param_2)

{
  if (param_1 < 0) {
    *(char *)(((int)param_1 & 0xfU) + DAT_00584e40 + -4) = (char)(param_2 << 4);
  }
  else {
    *(char *)(DAT_00584e3c + param_1) = (char)(param_2 << 4);
  }
  return;
}

