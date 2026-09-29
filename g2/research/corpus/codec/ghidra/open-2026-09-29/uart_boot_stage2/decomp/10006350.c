
int gx8002_stage2_strnlen(char *param_1,int param_2)

{
  int iVar1;
  char *pcVar2;
  
  if (param_2 == 0) {
    iVar1 = 0;
  }
  else if (*param_1 == '\0') {
    iVar1 = 0;
  }
  else {
    pcVar2 = param_1;
    do {
      pcVar2 = pcVar2 + 1;
      if (pcVar2 == param_1 + param_2) break;
    } while (*pcVar2 != '\0');
    iVar1 = (int)pcVar2 - (int)param_1;
  }
  return iVar1;
}

