
undefined8 cff_index_get_sid_string(int param_1,uint param_2)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (param_2 == 0xffff) {
    uVar1 = 0;
  }
  else if (param_2 < 0x187) {
    if (*(int *)(param_1 + 0xc0c) == 0) {
      uVar1 = 0;
    }
    else {
      uVar1 = (**(code **)(*(int *)(param_1 + 0xc0c) + 0x14))();
    }
  }
  else {
    uVar1 = cff_index_get_string(param_1,param_2 - 0x187);
  }
  return CONCAT44(unaff_r7,uVar1);
}

