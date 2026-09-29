
void FUN_00415ffa(char *param_1,char *param_2)

{
  char cVar1;
  char *pcVar2;
  char *pcVar3;
  
  cVar1 = *param_2;
  if (cVar1 == '\0') {
    return;
  }
  do {
    param_1 = (char *)FUN_00417c64(param_1,cVar1);
    pcVar2 = param_1;
    pcVar3 = param_2;
    if (param_1 == (char *)0x0) {
      return;
    }
    do {
      pcVar3 = pcVar3 + 1;
      if (*pcVar3 == '\0') {
        return;
      }
      pcVar2 = pcVar2 + 1;
    } while (*pcVar2 == *pcVar3);
    param_1 = param_1 + 1;
  } while( true );
}

