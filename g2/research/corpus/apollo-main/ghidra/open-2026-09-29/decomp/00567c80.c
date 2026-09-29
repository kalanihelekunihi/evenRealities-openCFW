
void FUN_00567c80(char *param_1,char *param_2)

{
  char cVar1;
  
  for (; *param_1 != '\0'; param_1 = param_1 + 1) {
  }
  do {
    *param_1 = *param_2;
    cVar1 = *param_1;
    param_2 = param_2 + 1;
    param_1 = param_1 + 1;
  } while (cVar1 != '\0');
  return;
}

