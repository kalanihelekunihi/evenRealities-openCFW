
undefined4 FUN_004216b2(char *param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  while ((*param_2 != 0 && (*param_1 != '\0'))) {
    delay_us(10);
    *param_2 = *param_2 + -1;
  }
  return param_4;
}

