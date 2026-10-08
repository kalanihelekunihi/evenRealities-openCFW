# Reached dependencies and ordering

All direct comparisons execute authenticated stock bodies on one side and compiler-generated source segments on the other. Source execution at stock executable addresses is rejected. Only absent resident ROM delay entry 0x40 is returned synthetically; inputs are recorded. No poll/timer/TON/cache helper return is substituted.

| Stock entry | Existing source provider | Use |
|---|---|---|
| 41d1c0 | opencfw_hal_delay_us | bounded polls and boost settle calls |
| 42a04a | opencfw_pcm22_timer_service | pending timer completion; native 2b/7b and timer-stop chain |
| 41ccd6 | opencfw_pcm22_spot_timer_stop | selector5 matched-target early return |
| 42a1bc | event_a_power_ton_adjust | selectors5,11,21; deliberately absent from locked12 |
| 41d21c | opencfw_boot_control_delay_status_change | four-argument equality adapter |
| 41d246 | opencfw_hal_status_poll | adapter supplies fifth argument equal=1; not the four-argument entry itself |
| 41e22e | opencfw_pcm22_icache_disable | selector21, conditional on initial SCB I-cache flag |
| 41e1e8 | opencfw_boot_icache_enable | selector21 restore; helper may return1 when blocked |

The equality wait first reads (*address & mask), returns0 when equal, otherwise delays(1) up to count times and rereads. Exhaustion returns4. Selectors5/11 ignore it and reread actual status bit24 to decide whether to request HP. LP/HP switch polls cap at20; pending timer readiness caps at60 before actual service call. Those limits do not certify elapsed time or peripheral state.

Profile fields are not one atomic snapshot. Initial current VDDF/target VDDF/target VDDC are retained across timer service. Target CORE/TEMPCO fields are reread after service for global cache publication and again for register programming. Selector5 rereads timer-enabled after comparing last-state; changing it to0 suppresses both wait and service. Native child calls preserve this distinction.

Selector11 clears AOR bit6 before CPU bit3; selector5 clears CPU before AOR. Both set PWRSW bit25 before conditional HP switch. Selector11 loads CORE/VDDC, boosts VDDF then restores it, and adjusts TON last. Selector12 boosts VDDF, loads CORE, waits(50), restores VDDF, with no TON call. Selector21 sets continuation byte200271bc=1 before TON, boosts/restores VDDF, conditionally disables cache, sets PWRSW bits16 and25, waits(20), then requests cache restoration. Cache helper failure is ignored. Deferred body429da4..429df6 would load current profile CORE/VDDC and clear continuation; it is not newly bound here and is not reached by the selected fixture set. A complete deferred hardware-transition lifecycle remains outside this result.

Raw R0 is not a success status. Walker42a43a..42a4bc ignores the value immediately after BLX. Selector11 returns the target-profile word address because stock pops its scratch stack slot intoR0;5/12/21 pop packed low-voltage bytes. Other caller-scratch registers are not public interface guarantees.
