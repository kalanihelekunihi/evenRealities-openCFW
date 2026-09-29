
undefined4
case_write_controller_blocking(int *param_1,ushort *param_2,int param_3,undefined4 param_4)

{
  undefined4 uVar1;
  ushort *puVar2;
  int iVar3;
  ushort *puVar4;
  int *piVar5;
  ushort *puVar6;
  
  if (param_1[0x22] == 0x20) {
    if (((param_2 == (ushort *)0x0) || (param_3 == 0)) ||
       ((param_1[2] == 0x1000 && ((param_1[4] == 0 && (((uint)param_2 & 1) != 0)))))) {
      uVar1 = 1;
    }
    else {
      param_1[0x24] = 0;
      param_1[0x22] = 0x21;
      piVar5 = param_1;
      puVar6 = param_2;
      uVar1 = case_tick_word2();
      *(short *)(param_1 + 0x15) = (short)param_3;
      *(short *)((int)param_1 + 0x56) = (short)param_3;
      if ((param_1[2] == 0x1000) && (param_1[4] == 0)) {
        puVar2 = (ushort *)0x0;
        puVar4 = param_2;
      }
      else {
        puVar4 = (ushort *)0x0;
        puVar2 = param_2;
      }
      while( true ) {
        if (*(short *)((int)param_1 + 0x56) == 0) break;
        iVar3 = case_wait_condition(param_1,0x80,0,uVar1,param_4,uVar1,puVar2,piVar5,puVar6);
        if (iVar3 != 0) goto LAB_0800675c;
        if (puVar2 == (ushort *)0x0) {
          *(uint *)(*param_1 + 0x28) = *puVar4 & 0x1ff;
          puVar4 = puVar4 + 1;
          puVar2 = (ushort *)0x0;
        }
        else {
          *(uint *)(*param_1 + 0x28) = (uint)(byte)*puVar2;
          puVar2 = (ushort *)((int)puVar2 + 1);
        }
        *(short *)((int)param_1 + 0x56) = *(short *)((int)param_1 + 0x56) + -1;
      }
      iVar3 = case_wait_condition(param_1,0x40,0,uVar1,param_4,uVar1,puVar2,piVar5,puVar6);
      if (iVar3 == 0) {
        param_1[0x22] = 0x20;
        uVar1 = 0;
      }
      else {
LAB_0800675c:
        uVar1 = 3;
      }
    }
  }
  else {
    uVar1 = 2;
  }
  return uVar1;
}

