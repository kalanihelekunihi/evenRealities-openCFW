
undefined4
case_read_controller_blocking(int *param_1,ushort *param_2,int param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  ushort uVar3;
  ushort *puVar4;
  ushort *local_34;
  
  if (param_1[0x23] != 0x20) {
    return 2;
  }
  if (((param_2 == (ushort *)0x0) || (param_3 == 0)) ||
     ((param_1[2] == 0x1000 && ((param_1[4] == 0 && (((uint)param_2 & 1) != 0)))))) {
    return 1;
  }
  param_1[0x24] = 0;
  param_1[0x23] = 0x22;
  param_1[0x1b] = 0;
  uVar1 = case_tick_word2();
  *(short *)(param_1 + 0x17) = (short)param_3;
  *(short *)((int)param_1 + 0x5e) = (short)param_3;
  iVar2 = param_1[2];
  uVar3 = 0xff;
  if (iVar2 == 0x1000) {
    if (param_1[4] == 0) {
      uVar3 = (ushort)DAT_080064e8;
    }
    goto LAB_0800646c;
  }
  if (iVar2 == 0) {
    if (param_1[4] == 0) goto LAB_0800646c;
  }
  else {
    if (iVar2 != 0x10000000) {
      uVar3 = 0;
      goto LAB_0800646c;
    }
    if (param_1[4] != 0) {
      uVar3 = 0x3f;
      goto LAB_0800646c;
    }
  }
  uVar3 = 0x7f;
LAB_0800646c:
  *(ushort *)(param_1 + 0x18) = uVar3;
  if ((iVar2 == 0x1000) && (param_1[4] == 0)) {
    local_34 = (ushort *)0x0;
    puVar4 = param_2;
  }
  else {
    puVar4 = (ushort *)0x0;
    local_34 = param_2;
  }
  while( true ) {
    if (*(short *)((int)param_1 + 0x5e) == 0) {
      param_1[0x23] = 0x20;
      return 0;
    }
    iVar2 = case_wait_condition(param_1,0x20,0,uVar1,param_4);
    if (iVar2 != 0) break;
    if (local_34 == (ushort *)0x0) {
      *puVar4 = (ushort)*(undefined4 *)(*param_1 + 0x24) & uVar3;
      puVar4 = puVar4 + 1;
    }
    else {
      *(byte *)local_34 = (byte)*(undefined4 *)(*param_1 + 0x24) & (byte)uVar3;
      local_34 = (ushort *)((int)local_34 + 1);
    }
    *(short *)((int)param_1 + 0x5e) = *(short *)((int)param_1 + 0x5e) + -1;
  }
  return 3;
}

