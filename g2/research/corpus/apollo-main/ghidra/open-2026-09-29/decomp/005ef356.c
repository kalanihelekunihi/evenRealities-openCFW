
short * TT_Get_VMetrics(int param_1,undefined4 param_2,short param_3,short *param_4,short *param_5)

{
  short sVar1;
  undefined4 local_10;
  
  if (*(char *)(param_1 + 0x124) == '\0') {
    local_10 = param_4;
    if (*(short *)(param_1 + 0x174) == -1) {
      *param_4 = *(short *)(param_1 + 0xdc) - param_3;
      if ((int)*(short *)(param_1 + 0xdc) - (int)*(short *)(param_1 + 0xde) < 0) {
        sVar1 = *(short *)(param_1 + 0xde) - *(short *)(param_1 + 0xdc);
      }
      else {
        sVar1 = *(short *)(param_1 + 0xdc) - *(short *)(param_1 + 0xde);
      }
      *param_5 = sVar1;
    }
    else {
      *param_4 = *(short *)(param_1 + 0x1ba) - param_3;
      if ((int)*(short *)(param_1 + 0x1ba) - (int)*(short *)(param_1 + 0x1bc) < 0) {
        sVar1 = *(short *)(param_1 + 0x1bc) - *(short *)(param_1 + 0x1ba);
      }
      else {
        sVar1 = *(short *)(param_1 + 0x1ba) - *(short *)(param_1 + 0x1bc);
      }
      *param_5 = sVar1;
    }
  }
  else {
    local_10 = param_5;
    (**(code **)(*(int *)(param_1 + 0x21c) + 0x70))(param_1,1,param_2);
  }
  return local_10;
}

