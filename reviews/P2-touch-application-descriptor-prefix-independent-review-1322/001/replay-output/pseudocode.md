# Application prefix with actual descriptor registration

Original 3CA4 loads descriptor 200004CC and calls actual A3B0, then restores its frame. Its 10-byte body 3CA4..3CAE excludes adjacent NOP and literal. The initialized descriptor has entry3621, index byte one, data200009C0 and priority byte two. The previously inserted descriptor20000850 has priority255, so original A3B0 inserts the new descriptor at head20000F38, links its next field to20000850 and sets that node's predecessor to200004CC. All four link fields are asserted.

The bounded startup now executes this call along with prior object/settings/SysTick/clock helpers and reaches3D50. Four deeper storage calls and four later application dependencies remain controlled. Initialized descriptor bytes originate from the pinned flash data copy, not an injected descriptor. Synthetic external clock tables and physical dispatch/timing remain unresolved. No canonical admission or C implementation.
