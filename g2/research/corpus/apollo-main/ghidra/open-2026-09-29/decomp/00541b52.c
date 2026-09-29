
int FUN_00541b52(char *param_1,char *param_2)

{
  char cVar1;
  char *pcVar2;
  char *pcVar3;
  
  for (pcVar2 = param_1; pcVar3 = param_2, *pcVar2 != '\0'; pcVar2 = pcVar2 + 1) {
    do {
      if (*pcVar3 == '\0') goto LAB_00541b6e;
      cVar1 = *pcVar3;
      pcVar3 = pcVar3 + 1;
    } while (*pcVar2 != cVar1);
  }
LAB_00541b6e:
  return (int)pcVar2 - (int)param_1;
}

