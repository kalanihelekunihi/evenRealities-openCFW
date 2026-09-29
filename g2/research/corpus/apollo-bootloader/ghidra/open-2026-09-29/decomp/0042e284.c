
undefined4 event_callback_dispatch_42e284(void)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  uVar1 = bl_runtime_value();
  bl_runtime_call(uVar1,8);
  (*(code *)*DAT_0042e470)();
  uVar1 = bl_runtime_value();
  bl_runtime_call(uVar1,0x30);
  return unaff_r7;
}

