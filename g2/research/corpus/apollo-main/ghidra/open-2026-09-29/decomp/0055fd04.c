
bool semantic_TouchFrameHasTerminator(int param_1,undefined4 param_2)

{
  int iVar1;
  
  iVar1 = semantic_TouchFrameTerminator(param_2);
  return *(char *)(param_1 + iVar1) == '\x17';
}

