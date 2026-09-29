
int gx8002_stage2_strlen(char *param_1)

{
  int iVar1;
  char *pcVar2;
  
  pcVar2 = param_1;
  if (*param_1 == '\0') {
    iVar1 = 0;
  }
  else {
    do {
      pcVar2 = pcVar2 + 1;
    } while (*pcVar2 != '\0');
    iVar1 = (int)pcVar2 - (int)param_1;
  }
  return iVar1;
}

