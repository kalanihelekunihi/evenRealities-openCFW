
undefined8 cJSON_GetArrayItem(undefined4 param_1,int param_2)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (param_2 < 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = get_array_item();
  }
  return CONCAT44(unaff_r7,uVar1);
}

