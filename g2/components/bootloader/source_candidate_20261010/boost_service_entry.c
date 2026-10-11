/* Deep-sleep BL 0x41aa60 targets stock nullable callback wrapper 0x41cdb8. */
__attribute__((naked)) void boost_service(void)
{
    __asm__ volatile("b.w boost_service_wrapper");
}
