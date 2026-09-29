
char * FUN_100112d4(char *param_1,char *param_2)

{
  char cVar1;
  undefined4 *puVar2;
  char *pcVar3;
  char *pcVar4;
  char *pcVar5;
  char *pcVar6;
  
  puVar2 = DAT_10011340;
  if ((param_1 == (char *)0x0) &&
     (param_1 = (char *)*DAT_10011340, (char *)*DAT_10011340 == (char *)0x0)) {
    return (char *)0x0;
  }
  do {
    pcVar3 = param_1;
    pcVar5 = param_2;
    do {
      cVar1 = *pcVar5;
      if (cVar1 == '\0') {
        pcVar5 = pcVar3 + 1;
        if (*pcVar3 == '\0') {
          *DAT_10011340 = 0;
          return (char *)0x0;
        }
        do {
          pcVar6 = pcVar5;
          pcVar5 = pcVar6 + 1;
          pcVar4 = param_2;
          do {
            cVar1 = *pcVar4;
            if (*pcVar6 == cVar1) {
              if (*pcVar6 == '\0') {
                pcVar5 = (char *)0x0;
              }
              else {
                *pcVar6 = '\0';
              }
              *puVar2 = pcVar5;
              return pcVar3;
            }
            pcVar4 = pcVar4 + 1;
          } while (cVar1 != '\0');
        } while( true );
      }
      pcVar5 = pcVar5 + 1;
      param_1 = pcVar3 + 1;
    } while (*pcVar3 != cVar1);
  } while( true );
}

