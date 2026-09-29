
int FT_Stream_GetChar(int param_1)

{
  char cVar1;
  char *pcVar2;
  
  cVar1 = '\0';
  if (*(uint *)(param_1 + 0x20) < *(uint *)(param_1 + 0x24)) {
    pcVar2 = *(char **)(param_1 + 0x20);
    *(char **)(param_1 + 0x20) = pcVar2 + 1;
    cVar1 = *pcVar2;
  }
  return (int)cVar1;
}

