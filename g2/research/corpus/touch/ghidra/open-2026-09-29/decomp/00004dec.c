
void touch_pipeline_1aec_reset_object(int param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = *(int *)(param_2 + 0xc) + param_1 * 0x90;
  if (*(char *)(iVar1 + 0x7b) != '\a') {
    uVar2 = (uint)*(ushort *)(iVar1 + 0x38);
    while (uVar2 != 0) {
      touch_pipeline_1ac4_reset_one(param_1,uVar2 - 1,param_2);
      uVar2 = uVar2 - 1;
    }
  }
  return;
}

