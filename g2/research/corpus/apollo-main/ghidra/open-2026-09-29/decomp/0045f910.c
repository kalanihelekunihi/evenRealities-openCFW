
undefined8 FUN_0045f910(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 *puVar4;
  
  if ((param_1 != 0) && (iVar1 = *(int *)(param_1 + 0xc), iVar1 != 0)) {
    iVar2 = FUN_00450286(param_1);
    if (((*(char *)(iVar1 + 0xe8) == '\0') && (iVar3 = FUN_0045fcb2(iVar1), iVar3 == 0)) ||
       (((iVar2 != 0x3c && (iVar2 != 0x3d)) && (iVar2 != 0x3e)))) {
      if (iVar2 == 0x3c) {
        if ((*(int **)(param_1 + 0x10) != (int *)0x0) && (**(int **)(param_1 + 0x10) != 0)) {
          FUN_0045f58c(iVar1);
        }
      }
      else if (iVar2 == 0x3d) {
        puVar4 = (undefined4 *)FUN_0045f8e6(iVar1);
        if (puVar4 != (undefined4 *)0x0) {
          FUN_0045f60e(iVar1,*puVar4);
        }
      }
      else if (iVar2 == 0x3e) {
        if ((*(int **)(param_1 + 0x10) != (int *)0x0) &&
           (iVar2 = **(int **)(param_1 + 0x10), iVar2 != 0)) {
          iVar3 = FUN_0045f840(iVar1,iVar2);
          if ((iVar3 == 0) || (*(char *)(iVar3 + 0xb) != '\x01')) {
            FUN_0045f58c(iVar1,iVar2);
          }
          else {
            FUN_0045f73a(iVar1,iVar3);
          }
        }
      }
      else if (iVar2 == 0x40) {
        iVar2 = FUN_0045f6a8(iVar1);
        if ((iVar2 != 0) && (*(int *)(iVar2 + 0x18) != 0)) {
          (**(code **)(iVar2 + 0x18))(iVar2,iVar1,0x40,param_1,param_2,param_3,param_4);
        }
        iVar2 = FUN_0045f66a(iVar1);
        if ((iVar2 != 0) && (*(int *)(iVar2 + 0x18) != 0)) {
          (**(code **)(iVar2 + 0x18))(iVar2,iVar1,0x40,param_1);
        }
      }
      else {
        iVar3 = FUN_0045f8e6(iVar1);
        if ((iVar3 != 0) && (*(int *)(iVar3 + 0x18) != 0)) {
          (**(code **)(iVar3 + 0x18))(iVar3,iVar1,iVar2,param_1);
        }
      }
    }
    else {
      iVar1 = FUN_0045fbe6(iVar1,param_1);
      if (iVar1 == 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          param_2 = 0x481;
          param_3 = DAT_0045fe8c;
          FUN_0043d574(2,DAT_0045fe98,DAT_0045fe94,DAT_0045fe90,0x481,DAT_0045fe8c,iVar2);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_0045fe9c,DAT_0045fe9c,iVar2);
        }
      }
    }
  }
  return CONCAT44(param_3,param_2);
}

