
undefined8 TT_New_Context(int param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int local_10;
  
  local_10 = param_4;
  if (param_1 != 0) {
    uVar2 = *(undefined4 *)(param_1 + 8);
    uVar1 = ft_mem_alloc(uVar2,0x27c,&local_10);
    if ((local_10 == 0) && (local_10 = Init_Context(uVar1,uVar2), local_10 == 0)) goto LAB_005f45ca;
  }
  uVar1 = 0;
LAB_005f45ca:
  return CONCAT44(local_10,uVar1);
}

