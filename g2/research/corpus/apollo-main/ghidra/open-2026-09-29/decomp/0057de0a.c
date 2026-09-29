
undefined8 FUN_0057de0a(undefined4 param_1,int param_2,int param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int local_20;
  undefined4 local_1c;
  
  puVar1 = (undefined4 *)pvPortMalloc(0x204);
  local_20 = param_3;
  local_1c = param_4;
  if (puVar1 != (undefined4 *)0x0) {
    FUN_0043c0e4(puVar1,0x204,0);
    *puVar1 = param_1;
    if (param_2 != 0) {
      FUN_0044b728(puVar1 + 1,0x100,&DAT_0057de74,param_2);
    }
    if (param_3 != 0) {
      FUN_0044b728(puVar1 + 0x41,0x100,&DAT_0057de74,param_3);
    }
    local_1c = 0;
    local_20 = 2;
    FUN_004548ba(&LAB_0057de7c_1,&DAT_0057de78,0x2000,puVar1);
  }
  return CONCAT44(local_1c,local_20);
}

