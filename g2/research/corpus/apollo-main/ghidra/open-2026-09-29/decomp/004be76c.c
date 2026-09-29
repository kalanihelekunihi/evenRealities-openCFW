
undefined4 nusProcMsg(undefined2 *param_1)

{
  char cVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  cVar1 = *(char *)(param_1 + 1);
  if (cVar1 == '\x12') {
    if (*(char *)((int)param_1 + 3) == '\0') {
      DAT_004be9cc[3] = 1;
    }
    else {
      DAT_004be9cc[3] = 0;
    }
  }
  else if (cVar1 == '\x14') {
    nusProcCccState();
  }
  else if (cVar1 != '\'') {
    if (cVar1 == '(') {
      iVar2 = DmConnRole((char)*param_1);
      if (iVar2 == 1) {
        *DAT_004be9cc = 0;
      }
    }
    else if (cVar1 == -0x55) {
      DAT_004be9cc[3] = 0;
      AttsHandleValueNtf((char)*param_1,0x8a4,param_1[4],*(undefined4 *)(param_1 + 2));
    }
  }
  return unaff_r7;
}

