
undefined8 AttcDiscCharStart(undefined1 param_1,int param_2)

{
  undefined4 uVar1;
  
  *(undefined1 *)(param_2 + 0x12) = 0;
  *(undefined1 *)(param_2 + 0x13) = 0xff;
  uVar1 = DAT_0056c37c;
  AttcReadByTypeReq(param_1,*(undefined2 *)(param_2 + 0xe),*(undefined2 *)(param_2 + 0x10),2);
  return CONCAT44(1,uVar1);
}

