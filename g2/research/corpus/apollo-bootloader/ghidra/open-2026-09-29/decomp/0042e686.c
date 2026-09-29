
void event_callback_enqueue_42e686
               (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_14;
  undefined4 local_10;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (*DAT_0042e868 == 0) {
    elog_output(1,DAT_0042e84c,DAT_0042e848,DAT_0042e880,0x96,DAT_0042e87c);
  }
  else if ((*DAT_0042e838 != 0) &&
          (local_14 = param_2, local_10 = param_1,
          iVar1 = FUN_004168a2(*DAT_0042e838,&local_14,0,param_3), iVar1 != 0)) {
    elog_output(1,DAT_0042e84c,DAT_0042e848,DAT_0042e880,0xa0,DAT_0042e884,iVar1);
  }
  return;
}

