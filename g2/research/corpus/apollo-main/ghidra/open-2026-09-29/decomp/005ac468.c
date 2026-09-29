
undefined8 cff_get_ros(int param_1,undefined4 *param_2,undefined4 *param_3,undefined4 *param_4)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar3 = 0;
  iVar2 = *(int *)(param_1 + 0x2a4);
  if (iVar2 != 0) {
    if (*(int *)(iVar2 + 0x5e0) == 0xffff) {
      uVar3 = 6;
    }
    else {
      if (param_2 != (undefined4 *)0x0) {
        if (*(int *)(iVar2 + 0xc18) == 0) {
          uVar1 = cff_index_get_sid_string(iVar2,*(undefined4 *)(iVar2 + 0x5e0));
          *(undefined4 *)(iVar2 + 0xc18) = uVar1;
        }
        *param_2 = *(undefined4 *)(iVar2 + 0xc18);
      }
      if (param_3 != (undefined4 *)0x0) {
        if (*(int *)(iVar2 + 0xc1c) == 0) {
          uVar1 = cff_index_get_sid_string(iVar2,*(undefined4 *)(iVar2 + 0x5e4));
          *(undefined4 *)(iVar2 + 0xc1c) = uVar1;
        }
        *param_3 = *(undefined4 *)(iVar2 + 0xc1c);
      }
      if (param_4 != (undefined4 *)0x0) {
        *param_4 = *(undefined4 *)(iVar2 + 0x5e8);
      }
    }
  }
  return CONCAT44(param_4,uVar3);
}

