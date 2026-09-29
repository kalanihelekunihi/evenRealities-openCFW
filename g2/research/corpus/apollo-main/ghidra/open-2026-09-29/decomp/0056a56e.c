
undefined4
hciEvtParseLePerAdvSyncEst(int param_1,undefined1 *param_2,undefined4 param_3,undefined4 param_4)

{
  *(undefined1 *)(param_1 + 4) = *param_2;
  *(ushort *)(param_1 + 6) = (ushort)(byte)param_2[2] * 0x100 + (ushort)(byte)param_2[1];
  *(undefined1 *)(param_1 + 8) = param_2[3];
  *(undefined1 *)(param_1 + 9) = param_2[4];
  FUN_004d293c(param_1 + 10,param_2 + 5);
  *(undefined1 *)(param_1 + 0x10) = param_2[0xb];
  *(ushort *)(param_1 + 0x12) = (ushort)(byte)param_2[0xd] * 0x100 + (ushort)(byte)param_2[0xc];
  *(undefined1 *)(param_1 + 0x14) = param_2[0xe];
  *(undefined1 *)(param_1 + 3) = *(undefined1 *)(param_1 + 4);
  return param_4;
}

