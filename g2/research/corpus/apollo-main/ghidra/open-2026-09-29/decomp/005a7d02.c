
undefined8 af_face_globals_get_metrics(int *param_1,uint param_2,uint param_3,int *param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int local_28;
  int *piStack_24;
  
  piVar1 = (int *)0x0;
  local_28 = 0;
  if (param_2 < (uint)param_1[1]) {
    if (((param_3 & 0xff) == 0x40) || (0x53 < (param_3 & 0xff) + 1)) {
      param_3 = (uint)*(ushort *)(param_1[2] + param_2 * 2);
    }
    iVar4 = *(int *)(DAT_005a7fa8 + (param_3 & 0xff) * 4);
    iVar2 = *(int *)(DAT_005a7fb0 + (uint)*(byte *)(iVar4 + 1) * 4);
    piVar1 = (int *)param_1[(param_3 & 0xff) + 4];
    if (piVar1 == (int *)0x0) {
      uVar3 = *(undefined4 *)(*param_1 + 100);
      piStack_24 = param_4;
      piVar1 = (int *)ft_mem_alloc(uVar3,*(undefined4 *)(iVar2 + 4),&local_28);
      if (local_28 == 0) {
        *piVar1 = iVar4;
        piVar1[9] = (int)param_1;
        if ((*(int *)(iVar2 + 8) == 0) ||
           (local_28 = (**(code **)(iVar2 + 8))(piVar1,*param_1), local_28 == 0)) {
          param_1[(param_3 & 0xff) + 4] = (int)piVar1;
        }
        else {
          if (*(int *)(iVar2 + 0x10) != 0) {
            (**(code **)(iVar2 + 0x10))(piVar1);
          }
          ft_mem_free(uVar3,piVar1);
          piVar1 = (int *)0x0;
        }
      }
    }
  }
  else {
    local_28 = 6;
  }
  *param_4 = (int)piVar1;
  return CONCAT44(local_28,local_28);
}

