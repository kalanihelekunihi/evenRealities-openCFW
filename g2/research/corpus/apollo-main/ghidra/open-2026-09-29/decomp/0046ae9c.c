
void system_close_page_factory_0046ae9c
               (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  local_20 = param_1;
  local_1c = param_2;
  uStack_18 = param_3;
  uStack_14 = param_4;
  FUN_0043c0e4(&local_20,10,0);
  FUN_0043c0e4(&local_20,10,0);
  local_20 = CONCAT13((char)((uint)param_2 >> 0x10),
                      CONCAT12((char)((uint)param_2 >> 8),CONCAT11((char)param_2,(char)param_1)));
  local_1c = CONCAT31(local_1c._1_3_,(char)((uint)param_2 >> 0x18));
  FUN_00464d1c(0x22,&local_20,5,0);
  return;
}

