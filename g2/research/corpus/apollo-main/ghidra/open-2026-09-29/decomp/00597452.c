
void td_record_status_write(undefined1 param_1)

{
  undefined4 uVar1;
  
  uVar1 = td_counter_b_get();
  td_record_status_set(uVar1,param_1);
  return;
}

