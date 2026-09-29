
int FUN_004157f8(char *param_1,char *param_2)

{
  char cVar1;
  char *pcVar2;
  char *pcVar3;
  
  for (pcVar2 = param_1; pcVar3 = param_2, *pcVar2 != '\0'; pcVar2 = pcVar2 + 1) {
    while (*pcVar3 != '\0') {
      cVar1 = *pcVar3;
      pcVar3 = pcVar3 + 1;
      if (*pcVar2 == cVar1) goto LAB_00415814;
    }
  }
LAB_00415814:
  return (int)pcVar2 - (int)param_1;
}

