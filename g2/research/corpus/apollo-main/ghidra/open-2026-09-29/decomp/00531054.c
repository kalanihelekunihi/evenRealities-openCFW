
void attcSendWriteCmd(int *param_1)

{
  attcSendSimpleReq(param_1);
  if ((int)((uint)*(byte *)(*param_1 + (uint)*(byte *)((int)param_1 + 0xe) * 4 + 2) << 0x1e) < 0) {
    attcSetPendWriteCmd(param_1);
  }
  else {
    attcExecCallback(*(undefined1 *)(*param_1 + 0xe),10,(short)param_1[3],0);
  }
  *(undefined1 *)((int)param_1 + 6) = 0;
  return;
}

