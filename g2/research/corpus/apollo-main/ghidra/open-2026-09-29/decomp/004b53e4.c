
undefined8 attcProcMultiVarNtf(int *param_1,short param_2,int param_3,uint param_4)

{
  ushort local_18;
  undefined1 local_16;
  undefined1 local_15;
  int local_14;
  short local_10;
  undefined2 uStack_e;
  uint local_c;
  
  local_16 = (undefined1)((*(byte *)(param_3 + 8) & 0xfffffffe) / 2);
  local_14 = param_3 + 9;
  _local_10 = CONCAT22((short)((uint)param_3 >> 0x10),param_2 + -1);
  local_18 = (ushort)*(byte *)(*param_1 + 0xe);
  local_15 = 0;
  local_c = param_4 & 0xffffff00;
  if (*(int *)(DAT_004b599c + 0x58) != 0) {
    (**(code **)(DAT_004b599c + 0x58))(&local_18);
  }
  *(byte *)(*param_1 + (uint)*(byte *)(param_1 + 10) * 4 + 2) =
       *(byte *)(*param_1 + (uint)*(byte *)(param_1 + 10) * 4 + 2) | 0x10;
  return CONCAT44(local_14,CONCAT13(local_15,CONCAT12(local_16,local_18)));
}

