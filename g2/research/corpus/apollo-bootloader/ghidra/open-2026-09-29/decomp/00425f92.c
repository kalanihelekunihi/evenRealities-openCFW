
int queue_transaction_call(void)

{
  int iVar1;
  int unaff_r5;
  
  iVar1 = sched_hiprio();
  if (iVar1 == 0) {
    *(undefined4 *)(unaff_r5 + 0x844) = 0;
  }
  return iVar1;
}

