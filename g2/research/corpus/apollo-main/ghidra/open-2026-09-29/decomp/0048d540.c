
char * FUN_0048d540(char *param_1,char *param_2)

{
  char cVar1;
  char *pcVar2;
  
  cVar1 = *param_2;
  pcVar2 = param_1;
  while( true ) {
    param_2 = param_2 + 1;
    *pcVar2 = cVar1;
    if (cVar1 == '\0') break;
    cVar1 = *param_2;
    pcVar2 = pcVar2 + 1;
  }
  return param_1;
}

