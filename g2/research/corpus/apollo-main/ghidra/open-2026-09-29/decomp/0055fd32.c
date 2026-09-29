
undefined4
semantic_TouchFrameSetChecksum
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  uVar1 = semantic_TouchFramePayload(param_2);
  semantic_TouchFrameWriteU16(param_1,uVar1,param_3);
  return param_4;
}

