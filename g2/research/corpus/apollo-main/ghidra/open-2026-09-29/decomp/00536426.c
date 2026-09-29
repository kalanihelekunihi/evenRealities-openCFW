
undefined8
FUN_00536426(undefined4 param_1,undefined4 param_2,undefined1 param_3,undefined4 param_4,
            undefined1 param_5)

{
  undefined1 uVar1;
  undefined2 *puVar2;
  uint uVar3;
  
  puVar2 = (undefined2 *)WsfMsgAlloc(0x38);
  if (puVar2 == (undefined2 *)0x0) {
    uVar3 = 0xff;
  }
  else {
    uVar1 = FUN_005363fc();
    *(undefined1 *)((int)puVar2 + 3) = uVar1;
    *puVar2 = (short)param_4;
    *(undefined1 *)(puVar2 + 1) = param_5;
    *(undefined1 *)(puVar2 + 0x1a) = 0;
    WsfMsgEnq(DAT_0053649c,param_3,puVar2);
    HciLeEncryptCmd(param_1,param_2);
    uVar3 = (uint)*(byte *)((int)puVar2 + 3);
  }
  return CONCAT44(param_4,uVar3);
}

