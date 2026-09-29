
undefined8 hciCmdAlloc(undefined2 param_1,short param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  
  puVar1 = (undefined1 *)WsfMsgAlloc(param_2 + 3);
  if (puVar1 != (undefined1 *)0x0) {
    *puVar1 = (char)param_1;
    puVar1[1] = (char)((ushort)param_1 >> 8);
    puVar1[2] = (char)param_2;
  }
  return CONCAT44(param_4,puVar1);
}

