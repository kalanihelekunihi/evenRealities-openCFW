
undefined4 SmpDmMsgSend(undefined4 param_1)

{
  undefined4 unaff_r7;
  
  WsfMsgSend(*(undefined1 *)(DAT_00537ebc + 0xec),param_1);
  return unaff_r7;
}

