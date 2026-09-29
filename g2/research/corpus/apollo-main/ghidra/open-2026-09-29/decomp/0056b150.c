
void hciEvtProcessCmdStatus(char *param_1)

{
  char cVar1;
  
  cVar1 = param_1[1];
  if (*param_1 != '\0') {
    hciEvtCmdStatusFailure(*param_1,(uint)(byte)param_1[3] * 0x100 + (uint)(byte)param_1[2]);
  }
  hciCmdRecvCmpl(cVar1);
  return;
}

