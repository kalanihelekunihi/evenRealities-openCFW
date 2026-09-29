
void attcReqClear(undefined1 param_1,int param_2,undefined1 param_3)

{
  attcFreePkt(param_2);
  attcExecCallback(param_1,*(undefined1 *)(param_2 + 2),*(undefined2 *)(param_2 + 8),param_3);
  *(undefined1 *)(param_2 + 2) = 0;
  return;
}

