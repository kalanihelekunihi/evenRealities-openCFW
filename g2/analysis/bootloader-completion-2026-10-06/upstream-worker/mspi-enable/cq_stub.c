/* Link-time stand-in only. The verifier intercepts this address and supplies
 * no queue behavior; it records the exact call boundary and arguments. */
__attribute__((section(".cq_provider"), noinline))
void mspi_cq_init(unsigned module, unsigned queue_argument,
                  unsigned queue_context)
{
    (void)module;
    (void)queue_argument;
    (void)queue_context;
}
