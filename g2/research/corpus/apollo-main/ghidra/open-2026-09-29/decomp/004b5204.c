
undefined8 AttGetMtu(undefined1 param_1)

{
  ushort *puVar1;
  undefined4 unaff_r7;
  
  puVar1 = (ushort *)attCcbByConnId(param_1);
  return CONCAT44(unaff_r7,(uint)*puVar1);
}

