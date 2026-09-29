
undefined8
dmConn2ActReadRemoteFeaturesCmpl(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  ushort local_18;
  undefined1 local_16;
  undefined1 local_15;
  undefined1 local_14;
  undefined1 uStack_13;
  undefined2 local_12;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_13 = (undefined1)((uint)param_2 >> 8);
  *(uint *)(param_1 + 0x28) =
       (uint)*(byte *)(param_2 + 9) * 0x100 + (uint)*(byte *)(param_2 + 8) +
       (uint)*(byte *)(param_2 + 10) * 0x10000 + (uint)*(byte *)(param_2 + 0xb) * 0x1000000;
  *(undefined1 *)(param_1 + 0x2c) = 1;
  local_16 = 0x57;
  local_18 = (ushort)*(byte *)(param_1 + 0x10);
  local_15 = 0;
  local_14 = *(undefined1 *)(param_2 + 4);
  local_12 = *(undefined2 *)(param_2 + 6);
  uStack_10 = param_3;
  uStack_c = param_4;
  FUN_00439be4(&uStack_10,param_2 + 8,8);
  (**(code **)(DAT_004b7430 + 0x9c))(&local_18);
  return CONCAT26(local_12,CONCAT15(uStack_13,
                                    CONCAT14(local_14,CONCAT13(local_15,CONCAT12(local_16,local_18))
                                            )));
}

