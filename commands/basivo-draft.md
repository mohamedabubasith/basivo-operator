---
description: Draft content on a site WITHOUT publishing — save a draft, verify it, return the draft URL. Never publishes.
argument-hint: <site> <content>   e.g. medium "<paste markdown>"  (title/tags/images inferred or asked)
---

Draft-only mode. Run the **browser-operator** engine but **stop after the draft
is saved and verified** — do NOT publish, submit, or send anything.

Input: `$ARGUMENTS`

1. Intake + Preflight + Session check as in `browser-operator`.
2. Use `content-to-web` to build the insertion plan (title/subtitle/body/tags/
   images).
3. Execute the site's **Create draft** flow only (see the site playbook). If the
   site has no server-side draft (e.g. LinkedIn feed posts), say so and stop with
   the composed content ready — do not post.
4. Verify the draft: reopen it, confirm title + body formatting + images, read
   the content back and diff against intent.
5. Report the **draft URL** and a short summary. Do NOT show a publish Safety
   Gate and do NOT publish, even if the content mentioned publishing.

If the user later wants it live, they run `/basivo-publish`.
