
void hciCoreTxAclComplete(undefined4 *param_1,int param_2)

{
  if (*(char *)((int)param_1 + 0x16) == '\0') {
    if (param_2 != 0) {
      WsfMsgFree();
    }
  }
  else if (*(short *)((int)param_1 + 0x12) == 0) {
    WsfMsgFree(*param_1);
    *param_1 = 0;
    *(undefined1 *)((int)param_1 + 0x16) = 0;
  }
  return;
}

