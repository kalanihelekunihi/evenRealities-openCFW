
void AttcDiscConfigStart(undefined1 param_1,int param_2)

{
  *(undefined1 *)(param_2 + 0x12) = 0;
  attcDiscConfigNext(param_1);
  return;
}

