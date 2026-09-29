
void FUN_00513f0c(short param_1,int param_2)

{
  if (param_1 < 0) {
    *(char *)(((int)param_1 & 0xfU) + DAT_00514248 + -4) = (char)(param_2 << 4);
  }
  else {
    *(char *)(DAT_00514244 + param_1) = (char)(param_2 << 4);
  }
  return;
}

