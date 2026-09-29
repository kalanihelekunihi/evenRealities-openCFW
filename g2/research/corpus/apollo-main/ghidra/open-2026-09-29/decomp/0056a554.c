
undefined1 * hciEvtParseLeScanReqRcvd(int param_1,undefined1 *param_2)

{
  *(undefined1 *)(param_1 + 4) = *param_2;
  *(undefined1 *)(param_1 + 5) = param_2[1];
  FUN_004d293c(param_1 + 6,param_2 + 2);
  return param_2 + 8;
}

