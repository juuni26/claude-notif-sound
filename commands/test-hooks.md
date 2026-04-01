---
description: "Test all 4 notification sound hooks sequentially. Use when the user wants to verify all hooks are working."
---

# Test Hooks

Test all 4 notification sound hooks sequentially. Follow these steps IN ORDER, waiting for each to complete before moving to the next:

**Step 1 - PermissionRequest hook:**
Run this bash command (do NOT auto-approve, let the user see the permission prompt):
```
echo "Hook 1/4: PermissionRequest triggered"
```
After the user approves, say "PermissionRequest hook done. Moving to step 2..."

**Step 2 - PreToolUse (AskUserQuestion) hook:**
Ask the user a question using the AskUserQuestion tool:
- Question: "Hook 2/4: Did you hear the PermissionRequest sound?"
- Options: "Yes" / "No"
Then say "AskUserQuestion hook done. Moving to step 3..."

**Step 3 - Notification hook:**
Run a long background bash command that takes 8 seconds, then say something after it finishes. This should trigger a desktop notification if the terminal is not focused:
```
sleep 8 && echo "Hook 3/4: Notification triggered (switch away from terminal to hear it)"
```
Tell the user to switch to another window during the wait so the notification fires.

**Step 4 - Stop hook:**
Say "All hooks tested! The Stop hook will fire now as I finish this response." Then stop responding. Do not ask any follow-up questions.
