
char * FUN_0057deb0(int param_1,undefined4 param_2,int *param_3)

{
  int iVar1;
  char *pcVar2;
  char *pcVar3;
  char *pcVar4;
  
  if (param_1 == 0) {
    param_1 = *param_3;
  }
  iVar1 = FUN_00541b52(param_1);
  pcVar4 = (char *)(param_1 + iVar1);
  if (*pcVar4 == '\0') {
    *param_3 = (int)&DAT_0057dee8;
    return (char *)0x0;
  }
  iVar1 = FUN_00541b30(pcVar4,param_2);
  pcVar2 = pcVar4 + iVar1;
  pcVar3 = pcVar2;
  if (*pcVar2 != '\0') {
    pcVar3 = pcVar2 + 1;
    *pcVar2 = '\0';
  }
  *param_3 = (int)pcVar3;
  return pcVar4;
}

