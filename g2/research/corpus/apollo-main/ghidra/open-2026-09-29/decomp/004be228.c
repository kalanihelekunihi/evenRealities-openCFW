
void essProcCccState(undefined2 *param_1)

{
  undefined1 *puVar1;
  
  puVar1 = DAT_004be38c;
  if (*(char *)(param_1 + 4) == '\x03') {
    if (param_1[3] == 1) {
      *DAT_004be38c = (char)*param_1;
      puVar1[2] = 1;
    }
    else {
      *DAT_004be38c = 0;
      puVar1[2] = 0;
    }
  }
  return;
}

