
void bleCccCback(undefined2 *param_1)

{
  int iVar1;
  int iVar2;
  
  if (((param_1[2] != 0) && (iVar1 = FUN_004bb07c((char)*param_1), iVar1 != 0)) &&
     (iVar2 = FUN_004bad26((char)*param_1), iVar2 != 0)) {
    FUN_0047b3e2(iVar1,*(undefined1 *)(param_1 + 4),param_1[3]);
  }
  iVar1 = WsfMsgAlloc(10);
  if (iVar1 != 0) {
    FUN_00439be4(iVar1,param_1,10);
    WsfMsgSend(*(undefined1 *)(DAT_004b81fc + 0x56),iVar1);
  }
  return;
}

