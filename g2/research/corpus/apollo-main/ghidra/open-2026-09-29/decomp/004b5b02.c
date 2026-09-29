
undefined1
GattWriteCback(undefined1 param_1,short param_2,undefined4 param_3,undefined2 param_4,
              undefined2 param_5,undefined4 param_6)

{
  undefined1 uVar1;
  
  if (param_2 == 0x15) {
    uVar1 = AttsCsfWriteFeatures(param_1,param_4,param_5,param_6);
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

