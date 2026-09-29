
undefined8 cff_free_glyph_data(int param_1,undefined4 *param_2,undefined4 param_3)

{
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  if (*(int *)(*(int *)(param_1 + 0x80) + 0x34) == 0) {
    cff_index_forget_element(*(int *)(param_1 + 0x2a4) + 0x4b4);
  }
  else {
    unaff_r5 = *param_2;
    (**(code **)(**(int **)(*(int *)(param_1 + 0x80) + 0x34) + 4))
              (*(undefined4 *)(*(int *)(*(int *)(param_1 + 0x80) + 0x34) + 4),&stack0xfffffff0);
    unaff_r6 = param_3;
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

