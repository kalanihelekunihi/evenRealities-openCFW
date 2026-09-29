
void gx8002_snpu_submit_task(int param_1)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  int iStack_14;
  
  piVar1 = piRam10205a8c;
  uVar3 = param_1 + 0x10;
  if (piRam10205a8c[0x170] == 0) {
    *piRam10205a8c = 1;
    uVar3 = uVar3 & 0xfffffff;
  }
  else {
    if (*piRam10205a8c != 2) {
      gx8002_snpu_task_cmd_cache_flush();
      iVar2 = piVar1[0x170];
      *(uint *)(iVar2 + 4) = uVar3 & 0x7ffffff;
      func_0x10025664(iVar2,8);
      goto LAB_10205a36;
    }
    gx8002_npu_get_over_cmd_addr(piRam10205a8c[0x171],&iStack_14);
    if (iStack_14 == 0) {
      uVar3 = uVar3 & 0x7ffffff;
    }
    else {
      *(uint *)(piVar1[0x170] + 4) = uVar3 & 0x7ffffff;
      uVar3 = *(uint *)(iStack_14 + 0x20000004);
      iStack_14 = iStack_14 + 0x20000000;
    }
    *piVar1 = 1;
  }
  gx8002_npu_set_task_head(piVar1[0x171],uVar3);
  gx8002_snpu_task_cmd_cache_flush(param_1);
  gx8002_npu_enable(piVar1[0x171]);
LAB_10205a36:
  piVar1[0x170] = param_1;
  return;
}

