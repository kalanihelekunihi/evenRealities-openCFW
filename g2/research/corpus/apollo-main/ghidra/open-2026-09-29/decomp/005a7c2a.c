
undefined8 af_face_globals_new(int param_1,undefined4 *param_2,int param_3,int param_4)

{
  int *piVar1;
  int local_18;
  
  local_18 = param_4;
  piVar1 = (int *)ft_mem_alloc(*(undefined4 *)(param_1 + 100),*(int *)(param_1 + 0x10) * 2 + 0x17c,
                               &local_18);
  if (local_18 == 0) {
    *piVar1 = param_1;
    piVar1[1] = *(int *)(param_1 + 0x10);
    piVar1[2] = (int)(piVar1 + 0x5f);
    piVar1[0x5e] = param_3;
    *(undefined2 *)(piVar1 + 0x58) = 0;
    piVar1[0x5b] = 0;
    piVar1[0x5c] = 0;
    piVar1[0x59] = 0;
    piVar1[0x5a] = 0;
    piVar1[0x5d] = 0;
    local_18 = af_face_globals_compute_style_coverage(piVar1);
    if (local_18 == 0) {
      piVar1[3] = 0;
    }
    else {
      af_face_globals_free(piVar1);
      piVar1 = (int *)0x0;
    }
  }
  *param_2 = piVar1;
  return CONCAT44(local_18,local_18);
}

