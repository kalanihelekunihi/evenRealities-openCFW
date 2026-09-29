
void AttcDiscConfigCmpl(undefined1 param_1,int param_2)

{
  *(char *)(param_2 + 0x12) = *(char *)(param_2 + 0x12) + '\x01';
  attcDiscConfigNext(param_1);
  return;
}

