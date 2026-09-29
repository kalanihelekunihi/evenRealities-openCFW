
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 terminal_query_reply_handler(int param_1,undefined4 param_2,undefined2 param_3)

{
  int iVar1;
  undefined1 *puVar2;
  int iVar3;
  
  terminal_action_lock();
  iVar1 = _DAT_005e4794;
  if (param_1 == 0) {
    iVar3 = APP_PbTerminalRxFrameDataProcess(param_2,param_3,_DAT_005e4794);
    puVar2 = _DAT_005e4798;
    if (iVar3 == 0xd) {
      *_DAT_005e4798 = 0;
      APP_PbTerminalTxEncodeCommResp(puVar2,*(undefined1 *)(iVar1 + 1));
    }
    else if (iVar3 == 0) {
      iVar3 = terminal_data_recv_handler(iVar1);
      if (iVar3 == 0) {
        *_DAT_005e4798 = 0;
      }
      else {
        *_DAT_005e4798 = 1;
      }
      APP_PbTerminalTxEncodeCommResp(_DAT_005e4798,*(undefined1 *)(iVar1 + 1));
    }
    else {
      *_DAT_005e4798 = 1;
      APP_PbTerminalTxEncodeCommResp(puVar2,*(undefined1 *)(iVar1 + 1));
    }
  }
  terminal_action_unlock();
  return 0;
}

