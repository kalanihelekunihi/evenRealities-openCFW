
void attExecCallback(byte param_1,undefined1 param_2,undefined2 param_3,undefined4 param_4,
                    undefined2 param_5)

{
  ushort local_20;
  undefined1 local_1e;
  undefined1 local_1d;
  undefined2 local_18;
  undefined2 local_16;
  undefined1 local_14;
  undefined2 local_12;
  undefined4 uStack_10;
  
  if (*(int *)(DAT_004b51d0 + 0x58) != 0) {
    local_20 = (ushort)param_1;
    local_1d = (undefined1)param_4;
    local_18 = 0;
    local_14 = 0;
    local_12 = param_5;
    local_1e = param_2;
    local_16 = param_3;
    uStack_10 = param_4;
    (**(code **)(DAT_004b51d0 + 0x58))(&local_20);
  }
  return;
}

