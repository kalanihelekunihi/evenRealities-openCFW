
undefined4 AttHandler(undefined4 param_1,int param_2)

{
  undefined4 unaff_r7;
  
  if (param_2 != 0) {
    if (*(byte *)(param_2 + 2) < 0x80) {
      if (*(byte *)(param_2 + 2) < 0x60) {
        if (*(byte *)(param_2 + 2) < 0x40) {
          if (*(byte *)(param_2 + 2) < 0x20) {
            (**(code **)(*(int *)(DAT_004b51d0 + 0x3c) + 8))();
          }
          else {
            (**(code **)(*(int *)(DAT_004b51d0 + 0x40) + 8))();
          }
        }
        else {
          (**(code **)(*(int *)(DAT_004b51d0 + 0x48) + 8))();
        }
      }
      else {
        (**(code **)(*(int *)(DAT_004b51d0 + 0x44) + 8))();
      }
    }
    else if (*(int *)(DAT_004b51d0 + 0x4c) != 0) {
      (**(code **)(DAT_004b51d0 + 0x4c))();
    }
  }
  return unaff_r7;
}

