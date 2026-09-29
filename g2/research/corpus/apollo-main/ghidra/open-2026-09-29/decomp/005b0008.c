
undefined4 cff_face_done(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  if (param_1 != 0) {
    uVar1 = *(undefined4 *)(param_1 + 100);
    if (*(int *)(param_1 + 0x21c) != 0) {
      (**(code **)(*(int *)(param_1 + 0x21c) + 0xc))(param_1);
    }
    if (*(int *)(param_1 + 0x2a4) != 0) {
      cff_font_done();
      ft_mem_free(uVar1,*(undefined4 *)(param_1 + 0x2a4));
      *(undefined4 *)(param_1 + 0x2a4) = 0;
    }
    cff_done_blend(param_1);
    *(undefined4 *)(param_1 + 700) = 0;
  }
  return param_4;
}

