
undefined8 FUN_00422dc6(uint *param_1,int param_2,int param_3,int param_4,int param_5)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_00423830)) {
    uVar1 = 2;
  }
  else {
    *(undefined1 *)(param_1 + 0x37) = 0;
    *(undefined1 *)((int)param_1 + 0xdd) = 0;
    if ((param_2 != 0) && (param_3 != 0)) {
      *(undefined1 *)(param_1 + 0x37) = 1;
      queue_init_4275ea(param_1 + 0xd,param_2,1,param_3);
    }
    if ((param_4 != 0) && (param_5 != 0)) {
      *(undefined1 *)((int)param_1 + 0xdd) = 1;
      queue_init_4275ea(param_1 + 0x13,param_4,1);
    }
    uVar1 = 0;
  }
  return CONCAT44(param_4,uVar1);
}

