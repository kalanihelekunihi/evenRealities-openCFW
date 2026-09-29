
undefined8
FUN_005d3ed0(int *param_1,undefined4 *param_2,int param_3,undefined4 param_4,int param_5,int param_6
            ,int param_7,int param_8,int param_9,int *param_10)

{
  int iVar1;
  int iVar2;
  
  FUN_0043c0e4(param_1,0x2e08,0);
  *param_1 = (int)param_2;
  param_1[1] = param_3;
  FUN_005d22f2(param_1 + 0xb57,*param_2,param_2 + 1,8);
  FUN_005d36b8(param_1 + 0x790,param_2,param_1 + 0x790,param_1 + 0xb57,param_4);
  FUN_005d36b8(param_1 + 0x3c9,param_2,param_1 + 0x790,param_1 + 0xb57,param_4);
  FUN_005d36b8(param_1 + 2,param_2,param_1 + 0x790,param_1 + 0xb57);
  param_1[0xb5f] = param_2[10];
  param_1[0xb60] = param_2[0xc];
  param_1[0xb61] = param_2[0xd];
  iVar1 = param_10[1];
  param_1[0xb62] = *param_10;
  param_1[0xb63] = iVar1;
  param_1[0xb65] = param_5;
  param_1[0xb66] = param_6;
  param_1[0xb67] = param_7;
  param_1[0xb68] = param_8;
  param_1[0xb69] = param_9;
  *(undefined1 *)((int)param_1 + 0x2d92) = *(undefined1 *)((int)param_2 + 0xb9);
  param_1[0xb6a] = param_2[0x39];
  param_1[0xb6b] = param_2[0x3a];
  if (param_1[0xb6b] < 0) {
    iVar1 = -param_1[0xb6b];
  }
  else {
    iVar1 = param_1[0xb6b];
  }
  if (param_1[0xb6a] < 0) {
    iVar2 = -param_1[0xb6a];
  }
  else {
    iVar2 = param_1[0xb6a];
  }
  if (iVar1 < iVar2) {
    if (param_1[0xb6a] < 0) {
      iVar1 = -param_1[0xb6a];
    }
    else {
      iVar1 = param_1[0xb6a];
    }
  }
  else if (param_1[0xb6b] < 0) {
    iVar1 = -param_1[0xb6b];
  }
  else {
    iVar1 = param_1[0xb6b];
  }
  param_1[0xb6c] = iVar1 << 1;
  param_1[0xb6d] = 0x199a;
  *(undefined1 *)((int)param_1 + 0x2d93) = 1;
  *(undefined1 *)(param_1 + 0xb64) = 0;
  *(undefined1 *)((int)param_1 + 0x2d91) = 0;
  *(undefined1 *)(param_1 + 0xb78) = 0;
  return CONCAT44(param_3,param_4);
}

