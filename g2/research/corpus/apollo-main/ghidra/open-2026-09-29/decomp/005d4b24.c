
undefined8 FUN_005d4b24(undefined4 *param_1,uint param_2)

{
  undefined4 unaff_r7;
  
  if (param_2 < 0x61) {
    param_1[2] = param_2;
    param_1[3] = param_1[2] + 7 >> 3;
    *(undefined1 *)(param_1 + 1) = 1;
    *(undefined1 *)((int)param_1 + 5) = 1;
  }
  else {
    FUN_005d2a0a(*param_1,0x12);
    param_2 = 0;
  }
  return CONCAT44(unaff_r7,param_2);
}

