# IAR Ubuntu download check — 2026-10-06

Native Safari MCP worked after the user enabled remote automation/external agents. The CLI is `/usr/bin/safaridriver --mcp` (Safari 27.2); initialize and tools/list succeeded. The installed connector catalog itself exposes no Safari tool, so discovery required the built-in CLI.

A plain WebDriver status query succeeded, but two bounded session-creation requests timed out without a session ID or returned permission denial. The owned diagnostic driver was stopped. No additional WebDriver session is pending from these attempts.

Supported MCP `page_info` returned no active tab; a restricted `list_tabs` selection exposed no IAR tab. `create_tab` opened only `https://updates.iar.com/?product=CXARM`, and `get_page_content` extracted its entire rendered page. The Ubuntu installer entry appears as text, has no interactive UID or URL, and has a valid-subscription requirement. Other actual release-note/device-patch links carry URLs/UIDs in the same extraction, so the missing installer target is meaningful. The package named in the install instructions is `cxarm-10.10.2.27058.deb`.

This is actual rendered Safari evidence, not merely a public HTTP scrape. It does **not** establish shared cookies/authentication with the user's preexisting signed-in Safari tab, and it does not prove the user's license lacks Ubuntu entitlement. An account-specific download URL is still unknown. Next user input needed: open the account's entitled product download page (or supply its normal page URL) in the authorized browser, or obtain the Linux package through IAR account/support. No guessed URL, cookie extraction, license-key access, credential entry, activation or security-setting change was performed.

The earlier Apple Events JavaScript attempt failed with Safari's explicit disabled-setting error. Native MCP text extraction avoided that mechanism; enabling Apple Events JavaScript is not required by this result.

Authenticated-context check: a persistent native MCP connection opened the requested IAR My Pages URL, which resolved to `https://mypages.iar.com/s/?language=en_US`. Its visible header contains a `Log in` control (node202), and no logout/signed-in account controls were found in that viewport. Thus the accessible automation context is not authenticated; ordinary user-tab authentication remains separate/unattached. The specific visible tab was left open for secure user sign-in. No credential-entry or login-submit tool action occurred. Persistent execution session44514 owns this MCP connection, awaiting user handoff.
