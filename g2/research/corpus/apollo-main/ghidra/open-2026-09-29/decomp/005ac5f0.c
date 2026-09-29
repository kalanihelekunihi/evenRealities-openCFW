
void cff_get_glyph_data(int param_1,undefined4 param_2,undefined4 *param_3,undefined4 *param_4)

{
  undefined4 *local_18;
  undefined4 *local_14;
  
  local_18 = param_3;
  local_14 = param_4;
  if (*(int *)(*(int *)(param_1 + 0x80) + 0x34) == 0) {
    cff_index_access_element(*(int *)(param_1 + 0x2a4) + 0x4b4,param_2,param_3,param_4);
  }
  else {
    (**(code **)**(undefined4 **)(*(int *)(param_1 + 0x80) + 0x34))
              (*(undefined4 *)(*(int *)(*(int *)(param_1 + 0x80) + 0x34) + 4),param_2,&local_18);
    *param_3 = local_18;
    *param_4 = local_14;
  }
  return;
}

