
void gx8002_snpu_overtime_reset(void)

{
  int iVar1;
  undefined4 local_20;
  int iStack_1c;
  int iStack_18;
  undefined4 local_14;
  
  iVar1 = DAT_10205bc4;
  gx8002_npu_get_base_addr(*(undefined4 *)(DAT_10205bc4 + 0x5cc),2,&local_20);
  gx8002_npu_get_cur_cmd_addr(*(undefined4 *)(iVar1 + 0x5c4),&iStack_1c);
  gx8002_npu_get_over_cmd_addr(*(undefined4 *)(iVar1 + 0x5c4),&iStack_18);
  gx8002_printf(PTR_s__SNPU__overtime_addr__0x_x__base_10205bc8,iStack_1c,local_20,iStack_18);
  gx8002_printf(PTR_s__SNPU__overtime_addr___0x80__10205bcc);
  gx8002_snpu_dump_words(iStack_1c + -0x80);
  gx8002_printf(PTR_s__SNPU__overtime_cmd___10205bd0);
  gx8002_snpu_dump_words((undefined1 *)(iStack_1c + 0x20000000));
  gx8002_printf(PTR_s_cmd_type__0x_x_10205bd4,*(undefined1 *)(iStack_1c + 0x20000000));
  if (iStack_18 == 0) {
    gx8002_npu_get_task_head(*(undefined4 *)(iVar1 + 0x5c4),&local_14);
  }
  else {
    local_14 = *(undefined4 *)(iStack_18 + 0x20000004);
  }
  gx8002_npu_disable(*(undefined4 *)(iVar1 + 0x5c4));
  gx8002_npu_reset(*(undefined4 *)(iVar1 + 0x5c8));
  gx8002_npu_regs_init();
  gx8002_npu_set_task_head(*(undefined4 *)(iVar1 + 0x5c4),local_14);
  gx8002_npu_enable(*(undefined4 *)(iVar1 + 0x5c4));
  return;
}

