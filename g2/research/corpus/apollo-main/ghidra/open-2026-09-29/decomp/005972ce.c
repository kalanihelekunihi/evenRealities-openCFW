
undefined4
td_record_build_from_event(byte *param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  undefined2 uVar2;
  
  if (param_1 == (byte *)0x0) {
    return param_4;
  }
  if (param_2 == (byte *)0x0) {
    return param_4;
  }
  *param_1 = *param_2;
  bVar1 = *param_2;
  if (bVar1 == 2) {
LAB_005972f2:
    param_1[1] = 1;
  }
  else {
    if (1 < bVar1) {
      if (bVar1 == 4) goto LAB_005972f2;
      if (bVar1 < 4) {
        param_1[1] = 2;
        goto LAB_00597302;
      }
    }
    param_1[1] = 0;
  }
LAB_00597302:
  uVar2 = td_bounded_string_copy(param_1 + 2,0x201,param_2 + 2);
  *(undefined2 *)(param_1 + 0x204) = uVar2;
  *(undefined4 *)(param_1 + 0x208) = param_3;
  return param_4;
}

