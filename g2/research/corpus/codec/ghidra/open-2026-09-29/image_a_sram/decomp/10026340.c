
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 gx8002_active_snpu_callback(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uStack_c;
  undefined4 uStack_8;
  
  uStack_c = param_1;
  uStack_8 = param_3;
  LvpQueuePut(_gx8002_active_snpu_queue_pointer,&uStack_c);
  return 0;
}

