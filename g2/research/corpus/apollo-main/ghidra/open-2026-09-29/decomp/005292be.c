
bool FUN_005292c8(char *param_1,char *param_2,uint param_3)

{
  do {
    *param_1 = *param_2;
    param_2 = param_2 + 1;
    param_1 = param_1 + 1;
    param_3 = param_3 - 1;
    if (param_3 < 2) break;
  } while (*param_2 != '\0');
  *param_1 = '\0';
  return *param_2 != '\0';
}

