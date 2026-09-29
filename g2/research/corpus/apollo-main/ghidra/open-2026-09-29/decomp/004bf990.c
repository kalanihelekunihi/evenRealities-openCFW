
void WsfMsgDataAlloc(short param_1,ushort param_2)

{
  WsfMsgAlloc(param_1 + (param_2 & 0xff));
  return;
}

