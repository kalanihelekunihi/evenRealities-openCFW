
undefined4
hciEvtParseLeEncryptCmdCmpl(int param_1,undefined1 *param_2,undefined4 param_3,undefined4 param_4)

{
  *(undefined1 *)(param_1 + 4) = *param_2;
  FUN_00439be4(param_1 + 5,param_2 + 1,0x10);
  *(undefined1 *)(param_1 + 3) = *(undefined1 *)(param_1 + 4);
  return param_4;
}

