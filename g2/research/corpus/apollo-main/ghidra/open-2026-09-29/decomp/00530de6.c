
undefined4
attcWriteCmdCallback(undefined1 param_1,int param_2,undefined1 param_3,undefined4 param_4)

{
  bool bVar1;
  
  bVar1 = false;
  while (!bVar1) {
    if (*(short *)(param_2 + 0x2a) != 0) {
      attcExecCallback(param_1,10,*(undefined2 *)(param_2 + 0x2a),param_3);
      *(undefined2 *)(param_2 + 0x2a) = 0;
    }
    bVar1 = true;
  }
  return param_4;
}

