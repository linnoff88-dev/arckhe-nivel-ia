# nivel-ia: What rung is AI on in your work?

[![AI Ladder: AL1 to AL5](guia/assets/banner-en.jpg)](https://inematds.github.io/nivel-ia/guia/en/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## What it is

Without measuring, you don’t know what you still do by hand, what AI already does on its own, or which doors you’ve opened for it. This kit gives you a five-rung scale, from AL1 (you do it yourself) to AL5 (AI runs on its own), and two ways to measure: a paper form that works for anyone and any AI, and a program that reads Claude Code and Codex records on your computer and notes every connection used. In the end, you’ll know which rung each task is on, which one can move up now, and when to move down. To get started, just print the form.

## 📖 User guide

Full guide (landing page + walkthrough): **https://inematds.github.io/nivel-ia/guia/en/**

## In detail

An open, free kit for measuring how much of your work AI already does, task by task, on the **AL1 to AL5 ladder**. Measure **on paper** (a form to print) or **automatically** (a program reads Claude Code and Codex records on your machine). Both record **all connections** the AI used and show **which tasks can move up a rung** and when to move down.

| Rung | What it means |
|---|---|
| AL1 | You do it yourself. AI isn’t involved. |
| AL2 | AI helps: you ask, it answers, you do the work. |
| AL3 | AI collaborates: you work together step by step, and you lead. |
| AL4 | AI leads, and you only review before it goes out. |
| AL5 | AI runs on its own, with a schedule, rules, and an alert. |

The complete ladder, including **how to move up each rung and when to move down**, is in [ESCADA.md](ESCADA.md) (in Portuguese).

## The process, from start to finish

Who does what: 🧠 you · ⚙️ script or timer

1. 🧠 **Read the ladder** and choose 3 tasks you do every week: [ESCADA.md](ESCADA.md) (in Portuguese).
2. 🧠 **On paper:** print the form (https://inematds.github.io/nivel-ia/kit/ficha-papel.en.html) and write one line per task (date, task, critical? y/n, rung 1 to 5, minutes, connection used, fixed? n/p/g, serious error? y/n). It works with any AI and for work you do without AI (AL1).
3. 🧠 **Enter the form data** (optional): copy `kit/papel-modelo.csv` to `registro/papel.csv`, open it in a spreadsheet, enter the rows, and save as CSV. Dates on the form must use yyyy-mm-dd (mm/dd/yyyy is read incorrectly). Check it with `python3 medir/nivel.py papel`. If you only use the form, you can skip steps 4 and 6: the report will use only the form data.
4. ⚙️ **Automatic:** `python3 medir/nivel.py varrer --dias 30` reads Claude Code and Codex logs from this machine and writes `registro/sessoes.json`.
5. ⚙️ **Report:** `python3 medir/nivel.py relatorio --lang en` builds the ladder, tasks, next rung for each task, connections, and “who can move up now” in `registro/relatorio.md` (and includes the paper form if one exists).
6. ⚙️ **All connections:** `python3 medir/nivel.py conexoes` lists each program, site, service, agent, and skill, with the first and last time it was used.
7. ⚙️ **Run automatically every day:** `sh systemd/instalar.sh` enables a timer at 06:20 that repeats steps 4 and 5 and saves the history in `registro/historico.jsonl`.
8. ⚙️ **Certificate:** `python3 medir/certificado.py --nome "Your Name" --lang en` generates `registro/certificado-AAAA-MM-DD-en.html`: rung, AL1–AL5 ladder, tasks, week-by-week progress, and projection (1, 3, and 6 months). Open it in a browser and use the button to save it as a PDF. Longer period: `nivel.py --registro /tmp/n90 varrer --dias 90`, `nivel.py --registro /tmp/n90 relatorio --lang en`, and `certificado.py --nome "Your Name" --lang en --registro /tmp/n90`.
9. 🧠 **Once a week:** read the report, choose ONE task to move up a rung (criteria in ESCADA.md) and move down a task that went badly.

## 🎓 Certificate: step by step

A page showing the percentage of your work handled by AI, the AL1–AL5 ladder, your main tasks, week-by-week progress, and projections for 1, 3, and 6 months. It's HTML: open it in any browser and turn it into a PDF with the "Save as PDF" button.

**Easiest way (Option B): ask your AI.** Open Claude Code or Codex and paste this (replace the name). Confidential data? Use the terminal method below (see Privacy).

> Download the kit from https://github.com/inematds/nivel-ia into a folder named nivel-ia (use it if it already exists), measure my last 30 days with `python3 medir/nivel.py varrer --dias 30` and `python3 medir/nivel.py relatorio --lang en`, generate my certificate with `python3 medir/certificado.py --nome "Your Name" --lang en`, and open the certificate in the browser. At the end, tell me where the certificate and report were saved and summarize the results in 3 lines. Do not open the file registro/sessoes.json and do not send my data to any other service or website.

**Do it yourself, one command at a time** (Linux or Mac; on Windows, WSL; Python 3.9+; must have used Claude Code or Codex on this machine):

```bash
git clone https://github.com/inematds/nivel-ia && cd nivel-ia
python3 medir/nivel.py varrer --dias 30          # 1. measures the last 30 days (nothing leaves the machine)
python3 medir/nivel.py relatorio --lang en                 # 2. builds the report
python3 medir/certificado.py --nome "Your Name" --lang en   # 3. generates the certificate
xdg-open registro/certificado-*.html             # 4. opens it (on Mac: open) → "Save as PDF" button
```

Longer period (e.g., 90 days), without changing the daily log: `python3 medir/nivel.py --registro /tmp/n90 varrer --dias 90`, `python3 medir/nivel.py --registro /tmp/n90 relatorio --lang en` and `python3 medir/certificado.py --nome "Your Name" --registro /tmp/n90`. Claude Code deletes records older than 30 days unless you increase `cleanupPeriodDays`; anything already deleted cannot be recovered. If the records cover fewer days than requested, the meter will warn you in the terminal, report, and certificate.

**Where the files are saved**

| File | What it is |
|---|---|
| `registro/certificado-AAAA-MM-DD-en.html` | The certificate (open in your browser → "Save as PDF") |
| `registro/relatorio.md` | The full report: ladder, tasks, next step, who can advance, connections |
| `registro/relatorio.json` | The same numbers as data (the certificate reads them from here) |
| `registro/sessoes.json` | The session-by-session measurement (only on your machine, outside git) |

## Requirements

Terminal, Python 3.9 or newer (standard library only, nothing to install), and git to download it (or download the ZIP: https://github.com/inematds/nivel-ia/archive/refs/heads/main.zip). Linux or macOS (on Windows, use WSL). The timer uses systemd (Linux). No network, no API: nothing leaves your machine.

## What automatic measurement sees and doesn’t see

- **Sees:** Claude Code sessions (`~/.claude/projects`) and Codex sessions (`~/.codex*/sessions`), how many messages you sent, how many AI actions, how much time, which programs, sites, services (MCP), agents, and skills it used, and which actions had an effect outside the machine (publishing, sending, uploading).
- **Doesn’t see:** what you do without AI (AL1: form only), other AIs (ChatGPT in a browser: form), whether you approved in the prompt, or whether the AI got it right (“fixed?” column on the form).
- **How it determines the rung:** a session started by a script, bot, or schedule (`claude -p`, `codex exec`) with up to 2 messages = AL5 (3 or more = conversation); a request you made through a bot (Telegram) = AL4; a conversation you had in the terminal: 15 or more AI actions per message from you = AL4, 5 to 14 = AL3, fewer = AL2 (a one-off question is AL2).
- **Moving up and down:** determined by the “fixed?” (n/p/g) and “serious error?” (y/n) columns on the form. AL1→AL2: no criteria; AL2→AL3: at most 1 major correction in the last 10 times; AL3→AL4: at most 2 in 20; AL4→AL5: at most 2 in 50 and no serious errors. Move down: 1 serious error or 3 major corrections in the last 10. Only instances at the current rung count (when the rung changes, the count starts over). A critical task (marked on the form or identified by words such as publish, client, server, email…) stops at AL4. Without a form, the report lists the task as a candidate and says how many times to record it. Details in [ESCADA.md](ESCADA.md) (in Portuguese). Limits are at the top of `medir/nivel.py`.
- **Tasks:** grouped by keywords from the first request. To use your own, copy `medir/tarefas.exemplo.json` to `medir/tarefas.json` and edit it (format `[["Task name", critical true/false, ["word", "another"]]]`). Critical tasks stop at AL4.

## Real example

[exemplo/relatorio-agregado.json](exemplo/relatorio-agregado.json) (in Portuguese): measurement of Nei Maldaner’s (INEMA) work over 30 days, totals only (no requests, folders, or sites).

## Tests

`python3 tests/run.py` (46 tests with fake logs; nothing from your machine).

## Privacy

**Two ways to run it.** The meter is pure Python and runs only on your machine, without internet access. **A. In the terminal**: you run the commands and open the certificate; nothing leaves your computer. **B. Ask your AI**: Claude Code or Codex runs the commands and reads the report to summarize it, and that reading goes through the provider’s server (Anthropic or OpenAI), like any other session. The report includes task names and connections (programs, agents, skills, and sites). These names may reveal the name of a client or project. **Confidential data (client work, NDA): use Option A.**

`registro/` is excluded from git. The first request from each session is stored in a shortened form, with keys, emails, and long numbers replaced by `[oculto]`.

MIT License · open and free kit · [inema.club](https://inema.club)