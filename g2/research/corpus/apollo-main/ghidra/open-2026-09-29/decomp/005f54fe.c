
undefined4 Ins_ENDF(int param_1)

{
  undefined4 *puVar1;
  undefined4 unaff_r7;
  
  if (*(int *)(param_1 + 0x1b0) < 1) {
    *(undefined4 *)(param_1 + 0xc) = 0x88;
  }
  else {
    *(int *)(param_1 + 0x1b0) = *(int *)(param_1 + 0x1b0) + -1;
    puVar1 = (undefined4 *)(*(int *)(param_1 + 0x1b8) + *(int *)(param_1 + 0x1b0) * 0x10);
    puVar1[2] = puVar1[2] + -1;
    *(undefined1 *)(param_1 + 0x17c) = 0;
    if ((int)puVar1[2] < 1) {
      Ins_Goto_CodeRange(param_1,*puVar1,puVar1[1]);
    }
    else {
      *(int *)(param_1 + 0x1b0) = *(int *)(param_1 + 0x1b0) + 1;
      *(undefined4 *)(param_1 + 0x16c) = *(undefined4 *)(puVar1[3] + 4);
    }
  }
  return unaff_r7;
}

