
undefined4 cJSON_Delete(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  while (param_1 != (int *)0x0) {
    iVar1 = *param_1;
    if ((-1 < param_1[3] << 0x17) && (param_1[2] != 0)) {
      cJSON_Delete(param_1[2]);
    }
    if ((-1 < param_1[3] << 0x17) && (param_1[4] != 0)) {
      (**(code **)(DAT_004d7f94 + 4))(param_1[4]);
    }
    if ((-1 < param_1[3] << 0x16) && (param_1[8] != 0)) {
      (**(code **)(DAT_004d7f94 + 4))(param_1[8]);
    }
    (**(code **)(DAT_004d7f94 + 4))(param_1);
    param_1 = (int *)iVar1;
  }
  return param_4;
}

