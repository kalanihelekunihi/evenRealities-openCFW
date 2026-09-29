
void semantic_TouchFrameChecksum(int param_1,undefined4 param_2)

{
  int iVar1;
  
  iVar1 = semantic_TouchFramePayload(param_2);
  semantic_TouchFrameReadU16(iVar1 + param_1);
  return;
}

