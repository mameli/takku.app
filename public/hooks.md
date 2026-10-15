# Installing a Takku Hook: a guide for coding agents

This page is for an AI agent (Claude Code, Codex, Copilot CLI, Cursor…) that a user asked to set up a Takku Hook on their Mac. The same guide for people: https://takku.app/hooks

Takku is a macOS menu bar app that records meetings, transcribes them on the Mac and writes a meeting note and a Transcript into the user's Obsidian vault. It has no integrations of its own: after each meeting it runs one executable, the Hook, and the Hook sends the meeting wherever the user wants. Source: https://github.com/mameli/Takku

The most common request is: "summarise my meetings with the assistant I already pay for". Takku can only send a meeting to an OpenAI-compatible API; a Hook can send it to a CLI instead (Copilot, Claude Code, Codex…), for example when the user's company allows only that tool.

## Rules

- **Ask before sending meetings anywhere.** Meetings hold other people's words. A meeting with a customer is usually the customer's data: many companies forbid sending it to any AI service without the customer's written consent. Default to an opt-in Hook (only the meetings the user marks), and let the user decide.
- **Never overwrite an existing Hook.** If `~/.takku/hooks/after-processing` exists, read it and keep it working (see "More than one hook").
- **Never write inside Takku's part of the note**, between `%% takku:start %%` and `%% takku:end %%`: Takku rewrites it on every Retry. Write next to it, or into a file of your own.
- **Run the AI tool with no tools of its own**, or the most restricted mode it has: the transcript is untrusted text, and a sentence said in a meeting must not be able to run commands. Never use `--yolo`, `--allow-all`, `--dangerously-*` or similar flags.
- **Test by hand** on a meeting the user picks before telling them it works.

## The contract

- **File**: exactly `~/.takku/hooks/after-processing`. A file, not a folder, no extension, executable (`chmod +x`), with a `#!` first line (`#!/bin/sh`, `#!/usr/bin/env python3`…). Its presence turns it on: there is no setting.
- **When**: after every meeting whose processing completes, and again after every successful Retry. Also when the user records with *Transcript* only (no Summary): then the note holds only a link to the Transcript.
- **Arguments**: `$1` is the absolute path of the meeting note, `$2` the absolute path of the Transcript.
- **Working directory**: the vault root. Notes are in `<vault>/Meetings/`, Transcripts in `<vault>/Meetings/Transcripts/`.
- **stdin**: `/dev/null`. stdout and stderr go together into `~/.takku/hooks/after-processing.log`, with the command to run that call again.
- **PATH**: Takku's own, usually `/usr/bin:/bin:/usr/sbin:/sbin` when it is started from Finder or at login, plus `/opt/homebrew/bin` and `/usr/local/bin`. Anything installed elsewhere (`~/.local/bin`, nvm, pyenv, asdf) is not found: call it by absolute path. Check with `command -v <tool>` in the user's shell and write the result into the Hook.
- **Time limit**: 5 minutes for the whole Hook. Then Takku sends SIGTERM to its process group and, 5 seconds later, SIGKILL.
- **Failure**: a non-zero exit shows a "Hook failed" notification. The meeting itself is never touched.
- **Permissions**: the Hook runs with Takku's macOS permissions (microphone, system audio, calendars).

## The files

The meeting note:

```markdown
---
takku_id: 6F1C2D4E-1111-4222-8333-944455556666
duration: 47m
language: it
transcript: "[[2026-10-15 1430 - Weekly sync (transcript)]]"
---
The user's own notes, taken during the meeting.

%% takku:start %%
Full transcript: [[2026-10-15 1430 - Weekly sync (transcript)]]
%% takku:end %%
```

- `takku_id` never changes: use it to update what an earlier run created instead of creating it twice.
- `summary_provider` and `template` are present only when Takku wrote a Summary itself. Without them, the meeting was recorded with *Transcript* only.
- The user can add their own properties (for example `copilot: true` or tags): Takku keeps them.
- The note may be renamed by Takku when it writes a Summary; find a meeting by `takku_id`, not by name.

The Transcript:

```markdown
---
takku_id: 6F1C2D4E-1111-4222-8333-944455556666
language: it
---
**[00:00] Me:** Let's go through the release.

**[00:15] Mario Rossi (Speaker 1):** The migration is done, the load tests are missing.
```

`Me` is the microphone. The others are `Speaker N`, `Name (Speaker N)` once named, or `Others` when the voices were not told apart.

## Steps: a Summary from the user's own AI subscription

1. **Look at what is there**: `ls -la ~/.takku/hooks/`. If `after-processing` exists, read it.
2. **Find the CLI** the user wants (`command -v copilot claude codex`, also `~/.local/bin`), and check it is logged in by running it once non-interactively.
3. **Ask the user**: which meetings may be sent (only those marked with a property, recommended; or all), which language, which sections. Tell them what they lose compared to Takku's own Summary: the Template, the Vocabulary in the prompt, the Speaker names taken from the Summary, and the title and rename of the note.
4. **Start from the ready-made Hook** for Copilot CLI: https://raw.githubusercontent.com/mameli/Takku/main/examples/hooks/copilot.sh. It sends only notes with `copilot: true`, builds the prompt from the user's notes and the Transcript, runs Copilot with every tool disabled in an empty folder, and writes `<note> - Copilot.md` next to the note. For another CLI, replace the `copilot` call (see below), rename the property and the output file, and use the CLI's absolute path.
5. **Install it**, at `~/.takku/hooks/after-processing`, or under its own name if there is already a Hook:
   ```sh
   mkdir -p ~/.takku/hooks
   curl -fsSL https://raw.githubusercontent.com/mameli/Takku/main/examples/hooks/copilot.sh -o ~/.takku/hooks/after-processing
   chmod +x ~/.takku/hooks/after-processing
   ```
6. **Tell the user to choose *Transcript* in Takku's menu** for the meetings this Hook summarises; otherwise Takku also writes its own Summary through its Summary Profile.
7. **Test it** on a meeting the user picks, with their consent to send it: add the property to that note, then run the Hook from the vault folder, with an environment close to Takku's:
   ```sh
   cd "/path/to/vault" && env -i HOME="$HOME" USER="$USER" PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin" \
     ~/.takku/hooks/after-processing "Meetings/<note>.md" "Meetings/Transcripts/<note> (transcript).md"
   ```
   Check the output file, how long it took (it must stay well under 5 minutes for the user's longest meetings), and `~/.takku/hooks/after-processing.log` after the next real meeting.

## Calling an AI CLI with no tools

Each takes the prompt and prints only the answer. Run it in an empty temporary folder (`cd "$(mktemp -d)"`) so it sees no files.

| CLI | Command | Notes |
|---|---|---|
| GitHub Copilot CLI | `copilot -p "$prompt" --silent --available-tools=none --disable-builtin-mcps --no-custom-instructions --no-ask-user --no-remote --no-auto-update` | `none` is no tool's name, so no tool is left. The prompt goes in an argument (macOS allows about 1 MB). Sessions are kept in `~/.copilot/`. |
| Claude Code | `printf '%s' "$prompt" \| claude -p --tools "" --strict-mcp-config --no-session-persistence` | Reads the prompt from stdin. Often installed in `~/.local/bin`: use the absolute path. |
| Codex | `printf '%s' "$prompt" \| codex exec --sandbox read-only --skip-git-repo-check --ephemeral --color never -o "$answer" -` | Codex keeps a shell, but read-only and without network. `-o` writes only the final answer into a file. |

Flags change between versions: check them with the CLI's `--help` before writing the Hook.

## More than one hook

Takku runs only `after-processing`. Keep each Hook in its own file in `~/.takku/hooks/` and make `after-processing` call them in turn:

```sh
#!/bin/sh
# ~/.takku/hooks/after-processing: runs the other hooks in turn
hooks="$HOME/.takku/hooks"
failed=0
"$hooks/notion.py" "$1" "$2" || failed=1
"$hooks/copilot.sh" "$1" "$2" || failed=1
exit $failed
```

The 5 minutes count for `after-processing` as a whole, the Hooks it calls included.
