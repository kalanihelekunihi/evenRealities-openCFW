
undefined4 dmConnSmActClose(int param_1,int param_2)

{
  undefined4 unaff_r7;
  
  HciDisconnectCmd(*(undefined2 *)(param_1 + 0xc),*(undefined1 *)(param_2 + 4));
  return unaff_r7;
}

