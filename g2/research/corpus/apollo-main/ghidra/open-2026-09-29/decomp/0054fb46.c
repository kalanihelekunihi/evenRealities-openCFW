
undefined4 FUN_0054fb46(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined1 auStack_34 [12];
  undefined1 auStack_28 [4];
  undefined1 auStack_24 [4];
  undefined1 auStack_20 [4];
  undefined1 auStack_1c [4];
  undefined1 auStack_18 [4];
  undefined1 auStack_14 [8];
  
  iVar1 = FUN_0054fa56(param_1,auStack_28,auStack_24,auStack_20,auStack_1c,auStack_18,auStack_14);
  if (iVar1 == 0) {
    iVar1 = service_time_calendar_to_epoch_wrapper(auStack_34);
    iVar3 = service_time_current_epoch_get();
    *param_2 = iVar3 - iVar1;
    uVar2 = 0;
  }
  else {
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

