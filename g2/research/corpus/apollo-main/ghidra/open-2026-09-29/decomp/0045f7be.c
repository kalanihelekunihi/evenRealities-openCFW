
undefined4
FUN_0045f7be(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (param_1 != (undefined4 *)0x0) {
    for (iVar1 = param_1[2]; iVar1 != 0; iVar1 = *(int *)(iVar1 + 0x20)) {
      FUN_00450500(*(undefined4 *)(iVar1 + 4),0);
    }
    for (iVar1 = param_1[3]; iVar1 != 0; iVar1 = *(int *)(iVar1 + 0x20)) {
      FUN_00450500(*(undefined4 *)(iVar1 + 4),0);
    }
    FUN_00451862(param_1[6],0x45f915);
    FUN_0045fbae(param_1 + 9);
    *(undefined1 *)(param_1 + 0x3a) = 0;
    *param_1 = 0;
    param_1[1] = 0;
    param_1[4] = 0;
    FUN_0044d7b8(param_1[6]);
    iVar1 = param_1[2];
    while (iVar1 != 0) {
      iVar1 = *(int *)(iVar1 + 0x20);
      file_heap_free();
    }
    iVar1 = param_1[3];
    while (iVar1 != 0) {
      iVar1 = *(int *)(iVar1 + 0x20);
      file_heap_free();
    }
    file_heap_free(param_1);
    FUN_0045bbd2();
  }
  return param_4;
}

