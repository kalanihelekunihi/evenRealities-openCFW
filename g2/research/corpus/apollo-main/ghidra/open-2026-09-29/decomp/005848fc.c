
char * FUN_005848fc(char *param_1,uint param_2,int *param_3)

{
  char *pcVar1;
  uint uVar2;
  
  uVar2 = 0;
  *param_3 = 0;
  while( true ) {
    if (param_2 <= uVar2) {
      return (char *)0x0;
    }
    for (; (*param_1 != '\0' && (*param_1 != ' ')); param_1 = param_1 + 1) {
    }
    for (; (*param_1 != '\0' && (*param_1 == ' ')); param_1 = param_1 + 1) {
    }
    if (*param_1 == '\0') break;
    uVar2 = uVar2 + 1;
    pcVar1 = param_1;
    if (uVar2 == param_2) {
      for (; (*pcVar1 != '\0' && (*pcVar1 != ' ')); pcVar1 = pcVar1 + 1) {
        *param_3 = *param_3 + 1;
      }
      if (*param_3 == 0) {
        param_1 = (char *)0x0;
      }
      return param_1;
    }
  }
  return (char *)0x0;
}

