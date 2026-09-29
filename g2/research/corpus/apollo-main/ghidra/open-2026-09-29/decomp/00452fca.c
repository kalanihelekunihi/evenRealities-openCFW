
void FUN_00452fca(char *param_1,undefined4 *param_2)

{
  *param_2 = 0;
  param_2[1] = 0;
  if ((param_1 != (char *)0x0) && ((*param_1 == '\x01' || (*param_1 == '\x03')))) {
    *param_2 = *(undefined4 *)(param_1 + 0x48);
    param_2[1] = *(undefined4 *)(param_1 + 0x4c);
  }
  return;
}

