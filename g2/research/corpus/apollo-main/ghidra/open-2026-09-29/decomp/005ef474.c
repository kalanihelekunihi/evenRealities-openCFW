
void tt_get_metrics_incr_overrides
               (int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int local_28 [3];
  undefined4 local_1c;
  undefined4 uStack_18;
  
  iVar1 = *param_1;
  if ((*(int *)(*(int *)(iVar1 + 0x80) + 0x34) != 0) &&
     (*(int *)(**(int **)(*(int *)(iVar1 + 0x80) + 0x34) + 8) != 0)) {
    local_28[0] = param_1[0xd];
    local_28[1] = 0;
    local_28[2] = param_1[0xe];
    local_1c = 0;
    uStack_18 = param_4;
    iVar1 = (**(code **)(**(int **)(*(int *)(iVar1 + 0x80) + 0x34) + 8))
                      (*(undefined4 *)(*(int *)(*(int *)(iVar1 + 0x80) + 0x34) + 4),param_2,0,
                       local_28);
    if (iVar1 == 0) {
      param_1[0xd] = (int)(short)local_28[0];
      param_1[0xe] = local_28[2] & 0xffff;
      param_1[0x2b] = 0;
      param_1[0x2c] = 0;
      if ((char)param_1[0x10] == '\0') {
        *(undefined1 *)(param_1 + 0x10) = 1;
        param_1[0xf] = local_28[2] & 0xffff;
      }
    }
  }
  return;
}

