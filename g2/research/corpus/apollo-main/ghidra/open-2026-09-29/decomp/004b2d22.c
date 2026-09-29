
undefined8 AppAdvStart(undefined4 *param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 local_c;
  
  puVar2 = param_1;
  local_c = param_4;
  iVar1 = appSlaveAdvMode();
  if (iVar1 != 0) {
    local_c = local_c & 0xffff0000;
    *(undefined1 *)(DAT_004b2dc8 + 0x57) = 0;
    param_2 = 1;
    puVar2 = &local_c;
    FUN_004b446a(1,(int)&local_c + 1,*DAT_004b2dcc + 6,*DAT_004b2dcc,puVar2,1,(uint)param_1 & 0xff);
  }
  return CONCAT44(param_2,puVar2);
}

