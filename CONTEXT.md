# FocusTimer

A desktop Pomodoro timer that runs focused work intervals and breaks in a fixed cycle, with an opt-in task feature for finding your way back after interruptions.

## Language

### Timer

**Pomodoro**:
One focused work interval, and also the name of the Mode it runs in. The two senses are deliberately the same word.
_Avoid_: Work session, focus block, round

**Mode**:
One of the three kinds of interval: Pomodoro, Short break or Long break. Each has its own duration and colours.
_Avoid_: Type, phase

**Break**:
A Short break or a Long break. Breaks are never interrupted and never logged.

**Cycle**:
The fixed sequence of Steps from the first Pomodoro to the Long break: N Pomodoros with a Short break after each but the last, which is followed by the Long break (P S P S P S P L for N = 4).
_Avoid_: Round, set

**Step**:
One slot in the Cycle, such as "Pomodoro 2 of 4" or the Long break.
_Avoid_: Stage, position

**Period**:
One run of the countdown in a Step, from full duration to zero. A Reset starts a new Period.
_Avoid_: Interval, timer (for this sense)

**Session**:
Everything that happens during one run of the app, from launch to close. The finished-Pomodoro count belongs to the Session.
_Avoid_: Cycle (they are different), day

**Finished**:
A Period that ran all the way to zero. A finished Pomodoro is **counted** at that moment.
_Avoid_: Completed, done (for Pomodoros; "Done" survives only as a log type)

**Skip**:
Leaving a Period that has not finished and moving to another Step. A skipped Pomodoro is not counted.

**Stopped**:
A Pomodoro that was started but left before it Finished, by Skip, Reset or changing Mode. It is not counted.
_Avoid_: Voided, abandoned, cancelled

**Next**:
Moving on from a Finished Period to the following Step, which starts immediately.
_Avoid_: Skip (for this case)

**Pause**:
Stopping the countdown with its remaining time kept, in any Mode.

**Resume**:
Restarting a paused countdown from its remaining time. Applies only to the timer, never to Tasks.
_Avoid_: Continue, Return (for this sense)

### Tasks (opt-in)

**Task**:
A short free-text description of what the user is working on. At most one Task is current at a time.
_Avoid_: Job, item, todo

**Completed**:
A Task the user has marked as done with ✓. Completing a Task does not affect the timer.
_Avoid_: Finished, done (for Tasks)

**Interruption**:
A Pause during a running Pomodoro, which offers the user a Note. Pausing a Break is not an Interruption.
_Avoid_: Pause (when the Note matters), break

**Note**:
The user's answer to "Where were you?" at an Interruption, shown after Resume as "↩ You were: …".
_Avoid_: Pause note, reason, comment

**Switch**:
Replacing the current Task with another while a Pomodoro is running. Any change to the Task text counts, including a typo fix.
_Avoid_: Change task, edit (for this sense)

**Park**:
To set the current Task and its Note aside on the parked stack so that another Task can become current.
_Avoid_: Shelve, suspend, save

**Return**:
To make a parked Task current again, together with its Note. Does not affect the timer.
_Avoid_: Resume (for Tasks), restore, unpark

**Work log**:
The append-only, human-readable history of Pomodoro and Task events, one file per calendar month.
_Avoid_: History, journal, report (a report is something built from the Work log)
