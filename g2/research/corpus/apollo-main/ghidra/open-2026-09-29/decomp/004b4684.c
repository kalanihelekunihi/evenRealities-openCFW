
void FUN_004b4684(undefined1 param_1)

{
  int iVar1;
  
  iVar1 = DmConnSecLevel(param_1);
  if (iVar1 == 0) {
    DmSecSlaveReq(param_1,*(undefined1 *)*DAT_004b471c);
  }
  return;
}

