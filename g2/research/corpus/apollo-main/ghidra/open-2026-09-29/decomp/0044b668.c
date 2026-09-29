
int elog_strcpy(uint param_1,char *param_2,char *param_3)

{
  char *pcVar1;
  
  if (param_2 == (char *)0x0) {
    if (*DAT_0044b714 == 0) {
      FUN_0043d574(0,DAT_0044b724,DAT_0044b720,DAT_0044b718,0x2c,DAT_0044b71c,&DAT_0044b70c,
                   DAT_0044b718,0x2c);
      do {
        FUN_0044b0ae();
      } while( true );
    }
    (*(code *)*DAT_0044b714)(&DAT_0044b70c,DAT_0044b718,0x2c);
  }
  pcVar1 = param_3;
  if (param_3 == (char *)0x0) {
    if (*DAT_0044b714 == 0) {
      FUN_0043d574(0,DAT_0044b724,DAT_0044b720,DAT_0044b718,0x2d,DAT_0044b71c,&DAT_0044b710,
                   DAT_0044b718,0x2d);
      do {
        FUN_0044b0ae();
      } while( true );
    }
    (*(code *)*DAT_0044b714)(&DAT_0044b710,DAT_0044b718,0x2d);
  }
  while ((*pcVar1 != '\0' && (param_1 < 0x400))) {
    *param_2 = *pcVar1;
    pcVar1 = pcVar1 + 1;
    param_2 = param_2 + 1;
    param_1 = param_1 + 1;
  }
  return (int)pcVar1 - (int)param_3;
}

