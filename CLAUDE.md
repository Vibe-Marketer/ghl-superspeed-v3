# Claude Code Instructions

## After completing any significant work, log it:

```python
# Run this to log your work to the Command Center
import urllib.request, json, base64
from datetime import datetime

GH_TOKEN = "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"

entry = {
    "repo": "drleadflow/ghl-superspeed-v3",
    "message": "DESCRIBE_WHAT_YOU_BUILT",
    "by": "claude-code",
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "details": "OPTIONAL_DETAILS"
}

# Append to blade-ops dev activity log
# (fetch current, prepend entry, push back)
```

## Project Context
- This is a Dr. Lead Flow project
- Owner: Blade (Emeka Ajufo)
- All work feeds into the Command Center at https://blade-command-center.vercel.app
- Log significant completions to blade-ops/logs/dev-activity.json

## Standards
- Commit messages should be descriptive
- After major features, update blade-ops/projects/ if relevant
- Reference blade-ops task files when completing tracked work
