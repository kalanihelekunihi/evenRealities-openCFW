
void semantic_TouchFrameSetTerminator(int param_1,undefined4 param_2)

{
  int iVar1;
  
  iVar1 = semantic_TouchFrameTerminator(param_2);
  *(undefined1 *)(param_1 + iVar1) = 0x17;
  return;
}

