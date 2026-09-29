
void cmdq_adapter_init_42c3e2(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint local_18;
  undefined4 local_14;
  undefined1 local_10;
  undefined3 uStack_f;
  undefined4 uStack_c;
  
  *(undefined4 *)(param_1 + 0x828) = 0;
  *(undefined4 *)(param_1 + 0x20) = 0;
  *(undefined4 *)(param_1 + 0x85c) = 0;
  local_18 = param_2 >> 1;
  _local_10 = CONCAT31((int3)((uint)param_3 >> 8),1);
  local_14 = param_3;
  uStack_c = param_4;
  iVar1 = am_hal_cmdq_init(*(uint *)(param_1 + 4) & 0xff,&local_18,param_1 + 0x828);
  if (iVar1 == 0) {
    *(undefined4 *)(param_1 + 0x20) = 0x100;
  }
  return;
}

