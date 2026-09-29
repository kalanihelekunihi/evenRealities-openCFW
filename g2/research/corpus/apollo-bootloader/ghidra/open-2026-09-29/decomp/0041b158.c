
int elog_strcpy(uint param_1,char *param_2,char *param_3)

{
  char *pcVar1;
  
  if (param_2 == (char *)0x0) {
    if (*DAT_0041b204 == 0) {
      elog_output(0,DAT_0041b214,DAT_0041b210,DAT_0041b208,0x2c,DAT_0041b20c,&DAT_0041b1fc,
                  DAT_0041b208,0x2c);
      do {
        FUN_0041ac8a();
      } while( true );
    }
    (*(code *)*DAT_0041b204)(&DAT_0041b1fc,DAT_0041b208,0x2c);
  }
  pcVar1 = param_3;
  if (param_3 == (char *)0x0) {
    if (*DAT_0041b204 == 0) {
      elog_output(0,DAT_0041b214,DAT_0041b210,DAT_0041b208,0x2d,DAT_0041b20c,&DAT_0041b200,
                  DAT_0041b208,0x2d);
      do {
        FUN_0041ac8a();
      } while( true );
    }
    (*(code *)*DAT_0041b204)(&DAT_0041b200,DAT_0041b208,0x2d);
  }
  while ((*pcVar1 != '\0' && (param_1 < 0x400))) {
    *param_2 = *pcVar1;
    pcVar1 = pcVar1 + 1;
    param_2 = param_2 + 1;
    param_1 = param_1 + 1;
  }
  return (int)pcVar1 - (int)param_3;
}

