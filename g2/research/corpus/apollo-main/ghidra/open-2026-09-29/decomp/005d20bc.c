
undefined8
FUN_005d20bc(int param_1,int param_2,undefined4 param_3,uint param_4,undefined4 param_5,
            undefined4 param_6,byte param_7,undefined1 param_8,undefined4 param_9)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_28;
  
  FUN_0043c0e4(param_1,0x5e8,0);
  iVar1 = ft_module_get_service(*(undefined4 *)(param_2 + 0x60),DAT_005d2820,1);
  if (iVar1 == 0) {
    uVar2 = 7;
    local_28 = param_4;
  }
  else {
    *(int *)(param_1 + 0x540) = iVar1;
    local_28 = (uint)param_7;
    FUN_005d128c(param_1,param_2,param_3,param_4);
    *(undefined4 *)(param_1 + 0x544) = *(undefined4 *)(param_2 + 0x10);
    *(undefined4 *)(param_1 + 0x548) = param_5;
    *(undefined1 *)(param_1 + 0x5bc) = param_8;
    *(undefined4 *)(param_1 + 0x5b8) = param_6;
    *(undefined4 *)(param_1 + 0x5c0) = param_9;
    FUN_00439c04(param_1 + 0x5c4,DAT_005d2824,0x10);
    uVar2 = 0;
  }
  return CONCAT44(local_28,uVar2);
}

