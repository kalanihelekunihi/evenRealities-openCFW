
void gx8002_clock_source_select(undefined4 *param_1)

{
  __reg_set_val(uRam10024bdc,*param_1,*(undefined1 *)(param_1 + 1),1);
  return;
}

