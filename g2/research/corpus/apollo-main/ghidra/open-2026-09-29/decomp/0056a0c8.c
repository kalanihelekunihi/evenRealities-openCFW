
undefined1 * hciEvtParseHwError(int param_1,undefined1 *param_2)

{
  *(undefined1 *)(param_1 + 4) = *param_2;
  return param_2 + 1;
}

