
undefined8 FUN_0042377c(uint *param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  uint uVar2;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_00423830)) {
    uVar1 = 2;
  }
  else {
    uVar2 = param_1[10];
    if (*(char *)((int)param_1 + 0x11b) == '\0') {
      if ((param_2 & 0x50) != 0) {
        FUN_00423608(param_1);
      }
      if ((int)(param_2 << 0x1a) < 0) {
        FUN_00423524(param_1);
      }
      if ((int)(param_2 << 0x1f) < 0) {
        *(undefined1 *)((int)param_1 + 0xde) = 1;
      }
    }
    else {
      if (param_1[0x3a] != 0) {
        *(uint *)param_1[0x3a] =
             param_1[0x39] - (*(uint *)(DAT_00423860 + uVar2 * 0x1000 + 0x50) & 0xfff);
      }
      if ((int)(param_2 << 0x19) < 0) {
        FUN_00422fde(param_1);
      }
      if ((int)(param_2 << 0x13) < 0) {
        FUN_00422d4c(param_1);
      }
      if ((int)(param_2 << 0x14) < 0) {
        if (param_1[0x3c] != 0) {
          uVar1 = FUN_00422d7a(uVar2,param_2);
          (*(code *)param_1[0x3c])(uVar1,param_1[0x3d]);
          param_1[0x3c] = 0;
        }
        FUN_00422d20(param_1);
      }
      *(undefined1 *)((int)param_1 + 0x11b) = 0;
    }
    uVar1 = 1;
  }
  return CONCAT44(param_4,uVar1);
}

