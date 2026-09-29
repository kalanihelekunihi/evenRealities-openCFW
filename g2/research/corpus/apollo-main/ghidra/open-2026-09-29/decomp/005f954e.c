
int tt_face_get_device_metrics(int param_1,uint param_2,int param_3)

{
  uint uVar1;
  
  uVar1 = 0;
  while( true ) {
    if (*(uint *)(param_1 + 0x2e4) <= uVar1) {
      return 0;
    }
    if (*(byte *)(*(int *)(param_1 + 0x2ec) + uVar1) == param_2) break;
    uVar1 = uVar1 + 1;
  }
  if (*(uint *)(param_1 + 0x2e8) <= param_3 + 2U) {
    return 0;
  }
  return *(int *)(param_1 + 0x2dc) + 8 + *(uint *)(param_1 + 0x2e8) * uVar1 + param_3 + 2U;
}

