---
title: The Limit — Prototype GDD (Tabletop Simulator build spec)
created: 2026-10-05
type: project
status: draft
tags: [board-game, the-limit, gdd, tts]
source: kaynak-The-Limit-orijinal.docx
---
# THE LIMIT — Prototype GDD v0.1

> **For the agent building this in Tabletop Simulator:** this file is the single source of truth.
> Every rule is written to be playable without guessing. Rules the original draft left open were
> resolved for the prototype and are marked **[A#]** (assumption #, listed in §12). Build exactly
> what is written; do not invent rules. If something is still unclear, list it in your report
> instead of deciding silently.

---

## 1. The game in one page

- **Players:** 3–5. **Length target:** 30–45 min.
- **Pitch:** Indebted strangers gamble in a mob-owned underground casino. Each round everyone pushes
  their luck for points; the lowest score is eliminated. To win you must survive to the final round
  **and** complete your secret objective.
- **Experience goal:** "Every card I draw could be the one that saves me or sinks me, and everyone
  at the table is watching me decide when to stop."
- **Core action:** On your turn, draw a card, then choose **PUSH** (draw again) or **CASH OUT**
  (lock your score and leave the round).
- **Escalation:** Each round adds more NPC Trigger cards to the Main Deck → more chaos, more
  player interaction.

---

## 2. Components (exact list)

| # | Component | Count | Notes |
|---|---|---|---|
| 1 | Main Deck | 50 base cards | Card list in §6 |
| 2 | Reserve NPC Trigger cards | 6 | Same as Main Deck NPC Triggers; added 2 per round (§4.1) |
| 3 | NPC Deck | 20 cards (all unique) | Card list in §7 |
| 4 | Character cards | 5 | §8 |
| 5 | Secret Objective cards | 5 | §9 |
| 6 | Score counter | 1 per player (5) | Shows current round score, min 0 |
| 7 | Objective progress counter | 1 per player (5) | Private bookkeeping for objectives (§9) |
| 8 | Round tracker | 1 track (rounds 1–4) + 1 marker | Track also shows NPC Trigger count per round |
| 9 | Status tokens | ~20 | CASHED OUT ×5, ENFORCED ×5, LOAN DEBT ×5, BODYGUARD ×5 |
| 10 | Ability-used tokens | 5 | Flip/place when a once-per-round/once-per-game ability is used |
| 11 | First player marker | 1 | |
| 12 | Player aid card | 5 | Turn flow summary (§5 condensed) |
| 13 | Board | 1 | Zones listed in §10 |

---

## 3. Setup

1. Shuffle the 5 Character cards; deal 1 face up to each player. Characters are public.
2. Shuffle the 5 Secret Objective cards **separately**; deal 1 face down to each player. Players
   look at their own objective only. Unused objectives go back to the box unseen. **[A1]**
3. Build the Main Deck: all 50 base cards (it already contains 6 NPC Triggers). Put the 6 Reserve
   NPC Triggers next to the Round Tracker. Shuffle the Main Deck.
4. Shuffle the NPC Deck.
5. Every player's score counter = 0, objective counter = 0.
6. Round marker on Round 1. Choose a random first player.

---

## 4. Game structure

### 4.1 Rounds

- The game lasts until 2 players remain, then one **Final Round** is played. **[A2]**
  - 5 players: Rounds 1–3 eliminate (5→4→3→2), Round 4 is the Final.
  - 4 players: Rounds 1–2 eliminate, Round 3 is the Final.
  - 3 players: Round 1 eliminates, Round 2 is the Final.
- **Start of each round:**
  1. All remaining players' scores = 0. Remove all status tokens. Reset once-per-round abilities.
  2. Collect all Main Deck cards (discard pile, set-aside cards, everything) and all NPC cards. **[A3]**
  3. From Round 2 on, add **2** Reserve NPC Triggers to the Main Deck each round:

     | Round | NPC Triggers in Main Deck | Main Deck size |
     |---|---|---|
     | 1 | 6 | 50 |
     | 2 | 8 | 52 |
     | 3 | 10 | 54 |
     | 4 | 12 | 56 |

  4. Shuffle Main Deck and NPC Deck.
  5. First player = player to the left of last round's first player (skip eliminated players).
- **Turns** go clockwise. A player who has CASHED OUT is skipped for the rest of the round.
  A player can have **many turns** in one round (CRASH and Negative cards end a turn, not the round).

### 4.2 End of round

The round ends immediately when **either**:
- every remaining player has CASHED OUT, **or** **[A4]**
- the Main Deck runs out. The current turn ends; every player keeps their current score.

Then:
- **Normal round:** the player with the **lowest** round score is eliminated (out of the game for good).
- **Tie for lowest:** tied players each draw from a freshly shuffled Main Deck, discarding until
  each reveals a Point Card. Lowest Point value is eliminated; repeat on a tie. **[A5]**
- **Final Round:** nobody is eliminated. Go to §4.3.

### 4.3 Winning

- A player wins only if they **reached the Final Round** and **completed their Secret Objective**.
- If several Final Round players completed their objective, the highest **Final Round score** wins.
  Tie = shared win.
- If no Final Round player completed their objective: **no winner** (the casino wins).

---

## 5. Turn flow (step by step)

```
START OF TURN
  - Apply start-of-turn effects (e.g. Survivor's +5).
  - Draw the top Main Deck card (or play your Smuggled card instead, see THE SMUGGLER).

RESOLVE THE CARD
  Point Card     → add value to score (apply DOUBLE if armed) → DECISION
  Negative Card  → subtract value (score min 0)                → TURN ENDS
  CRASH          → score = 0                                    → TURN ENDS (you stay in the round)
  Special Card   → follow its text; unless it says otherwise   → DECISION
  NPC Trigger    → draw 1 NPC card, resolve it; unless the NPC says otherwise → DECISION

DECISION (only if the turn did not end and no effect forces a draw)
  PUSH      → draw the next Main Deck card, resolve it.
  CASH OUT  → score is locked, take a CASHED OUT token. You take no more turns this round.
              Other players may now offer SHARE THE RISK (§11).
```

**Timing rules**
- "Forced" draws (FORCED PUSH, SECOND DRAW, THE GAMBLER, THE GAMBLING ADDICT, ENFORCED, LOAN DEBT)
  must be resolved before you may choose CASH OUT. If a forced card ends your turn (Negative/CRASH),
  the turn ends.
- Score never goes below 0. Any loss that would go below 0 sets it to 0.
- Every effect that "takes points" from another player can target **any** remaining player in the
  round, including players who already CASHED OUT. **[A6]** CASH OUT stops you drawing, it does not
  protect your points.
- **Out-of-turn draw:** when an effect makes a player draw a Main Deck card outside a normal turn
  (THE BOSS, SHARE THE RISK), only Point, Negative and CRASH cards apply to them. Any other card is
  discarded and another card drawn. Out-of-turn draws never end anybody's turn. **[A7]**
- A drawn card goes to the discard pile after it resolves, unless an effect keeps it on the table
  (SAFE PASS, SMUGGLER).

---

## 6. Main Deck — 50 base cards

Card IDs are for the TTS build. Card text below is the exact text to print.

### 6.1 Point Cards (24)

| ID | Name | Qty | Text |
|---|---|---|---|
| P05 | +5 | 8 | Gain 5 points. |
| P10 | +10 | 7 | Gain 10 points. |
| P20 | +20 | 5 | Gain 20 points. |
| P30 | +30 | 3 | Gain 30 points. |
| P50 | +50 | 1 | Gain 50 points. |

### 6.2 Negative Cards (8)

| ID | Name | Qty | Text |
|---|---|---|---|
| N05 | −5 | 3 | Lose 5 points. Your turn ends. |
| N10 | −10 | 3 | Lose 10 points. Your turn ends. |
| N20 | −20 | 2 | Lose 20 points. Your turn ends. |

### 6.3 CRASH (4)

| ID | Name | Qty | Text |
|---|---|---|---|
| CR | CRASH | 4 | Your round score becomes 0. Your turn ends. You stay in the round. |

### 6.4 Special Cards (8)

| ID | Name | Qty | Text |
|---|---|---|---|
| S-DBL | DOUBLE | 2 | Keep this in front of you. Your next Point Card this turn is doubled. Then discard this. (Discard at end of turn if unused.) |
| S-2ND | SECOND DRAW | 2 | Immediately draw another card and resolve it. |
| S-SAFE | SAFE PASS | 2 | Keep this in front of you. Once this turn, when you draw a Negative Card or CRASH, you may discard it unresolved and draw a new card. (Discard at end of turn if unused.) |
| S-STL | STEAL | 1 | Take 10 points from another player (all of them if they have fewer than 10). |
| S-FRC | FORCED PUSH | 1 | You must draw another card now. You cannot CASH OUT before resolving it. |

### 6.5 NPC Trigger (6 in base deck + 6 in reserve = 12 total)

| ID | Name | Qty | Text |
|---|---|---|---|
| T-NPC | DRAW AN NPC CARD | 6 (+6 reserve) | Draw 1 card from the NPC Deck and resolve it. Then continue your turn unless it says otherwise. |

**Deck check:** 24 + 8 + 4 + 8 + 6 = **50**.

---

## 7. NPC Deck — 20 cards

An NPC card is discarded after it resolves (except where it leaves a status token). If the NPC Deck
runs out, shuffle the NPC discard pile into a new NPC Deck.

| ID | Name | Text |
|---|---|---|
| NPC01 | THE BOOKMAKER | Choose another player. If their score is higher than yours, gain 15 points. |
| NPC02 | THE COLLECTOR | Choose another player. They lose 10 points; you gain 5 points. |
| NPC03 | THE DEALER | Draw 2 Main Deck cards. Resolve one; put the other on the bottom of the Main Deck. |
| NPC04 | THE FIXER | The next Negative Card you draw this turn has no effect (discard it; your turn continues). |
| NPC05 | THE INFORMANT | Look at the top 3 Main Deck cards and put them back in any order. |
| NPC06 | THE LOAN SHARK | Gain 30 points. Take a LOAN DEBT token: you must draw at least 2 more cards before you can CASH OUT. **[A8]** |
| NPC07 | THE SABOTEUR | Choose another player. They lose 10 points. |
| NPC08 | THE SMUGGLER | Put the top Main Deck card face down in front of you without looking. On a later turn this round, you may reveal and resolve it instead of drawing a card. If unused, it is shuffled back at round end. **[A3]** |
| NPC09 | THE INSPECTOR | Look at all face-down cards in front of another player (Smuggled card). If they have none, nothing happens. |
| NPC10 | THE GAMBLER | Draw 2 Main Deck cards and resolve both, one after the other. You cannot CASH OUT between them. |
| NPC11 | THE BODYGUARD | Take a BODYGUARD token. The next effect that would take away your points (Negative, CRASH, steal, any loss) is ignored. The token lasts until it is used or the round ends. **[A9]** |
| NPC12 | THE THIEF | Take 15 points from another player (all of them if they have fewer than 15). |
| NPC13 | THE DEALER'S ASSISTANT | Draw 1 Main Deck card. If it is a Point Card, gain 10 extra points. Otherwise resolve it normally. |
| NPC14 | THE BROKER | If you have at least 10 points, you may turn 10 of them into 20 (net +10). |
| NPC15 | THE BOSS | Choose one: gain 20 points, **or** make another player draw 1 Main Deck card (out-of-turn draw, §5). |
| NPC16 | THE CLEANER | Remove one ENFORCED or LOAN DEBT token from yourself. If you have none, gain 5 points. |
| NPC17 | THE GAMBLING ADDICT | You must draw another card now. If it is a Point Card, gain 10 extra points. |
| NPC18 | THE DRIVER | Give 10 of your points to another player (all of them if you have fewer than 10). **[A10]** |
| NPC19 | THE ENFORCER | Choose another player who has not CASHED OUT. They take an ENFORCED token: on their next turn they must draw at least 2 cards before they can CASH OUT. |
| NPC20 | THE INSIDER | Look at the top Main Deck card. Leave it on top or put it on the bottom. |

**Naming note:** four NPCs share names with Characters (Fixer, Thief, Gambler, Collector). In TTS,
print "NPC" in the card type line and use a different card back so they are never confused.

---

## 8. Characters — 5 cards (public)

| ID | Character | Ability | Playstyle |
|---|---|---|---|
| C1 | THE GAMBLER | **DOUBLE DOWN** (once per round): after you resolve a Point Card, declare Double Down: your next Point Card this turn is doubled. **[A11]** | Maximum risk |
| C2 | THE FIXER | **SECOND CHANCE** (once per game): when you draw CRASH, keep half your score (round down) instead of 0. Your turn still ends. | Control, caution |
| C3 | THE THIEF | **PICKPOCKET** (once per round): when a Special or NPC card lets you take points from another player, take 5 more. | Interfering |
| C4 | THE SURVIVOR | **NOT DEAD YET:** after you CRASH, gain 5 points at the start of your next turn. | Recovery |
| C5 | THE COLLECTOR | **CONNECTIONS** (once per round): the first time you resolve an NPC Trigger, draw 2 NPC cards, resolve one, put the other on the bottom of the NPC Deck. | NPC interaction |

---

## 9. Secret Objectives — 5 cards (hidden)

Players track progress on their **objective counter**. Once complete, keep it secret; reveal at game end.
Objectives can be completed in any round.

| ID | Objective | Exact condition | What counts |
|---|---|---|---|
| O1 | **ONE MORE** | In **3 different turns**, choose PUSH **3 or more times in a row** in that turn. **[A12]** | Only voluntary PUSH decisions count, not forced draws. |
| O2 | **CLEAN EXIT** | CASH OUT with **20 or more** points **3 times**. | Score at the moment you declare CASH OUT (before Share the Risk). |
| O3 | **TAKE WHAT ISN'T YOURS** | Take a total of **40 points** from other players over the game. | Points actually moved from another player into your score (STEAL, THE THIEF, PICKPOCKET bonus, THE COLLECTOR's 5). |
| O4 | **STILL STANDING** | **2 times**: suffer a CRASH, then reach **20+ points later in the same round**. | A CRASH cancelled by SAFE PASS or BODYGUARD does not count. The Fixer's half-score CRASH counts. |
| O5 | **COLLECTION** | Resolve **5 different NPC cards** yourself over the game. | NPCs you resolved (not ones you put on the bottom). Keep a private list. |

**3-player scaling:** in a 3-player game, any objective count of **3** becomes **2** (O1, O2),
because there are only 2 rounds. **[A13]**

---

## 10. Board / table layout (TTS)

Central board zones: Main Deck · Main discard · NPC Deck · NPC discard · Reserve NPC Triggers ·
Round Tracker (1–4 with NPC Trigger counts printed) · Eliminated players area.

Each player area: Character card (face up) · Secret Objective (face down, in hand zone) · Score
counter · Objective counter · space for kept cards (DOUBLE, SAFE PASS, Smuggled card) and status
tokens · Player aid.

---

## 11. SHARE THE RISK

1. When a player declares CASH OUT with **more than 0** points, any player who has **not** CASHED
   OUT yet may say "I'll share your risk." If several want to, the first one clockwise from the
   cashing player gets it. **[A14]**
2. The cashing player cannot refuse or cancel.
3. The sharer makes an out-of-turn draw (§5): only Point, Negative or CRASH applies; anything else is
   discarded and redrawn.
4. Apply the card to the **cashing player's** score, then split: each gets half, rounded down.
   - The cashing player's score = their half.
   - The sharer's score is **replaced** by their half, and the sharer is now also CASHED OUT. **[A14]**
5. No other effects apply during the share (no DOUBLE, SAFE PASS, BODYGUARD, abilities).

**Example.** A has 40 and cashes out. B has 5 and has not cashed out; B shares. B draws +20:
40 + 20 = 60 → A = 30, B = 30 (B's old 5 is gone), both CASHED OUT.
If B drew −20: 20 → A = 10, B = 10. If B drew CRASH: A = 0, B = 0.

**Why it exists:** a trailing player can trade their whole round for half of a leader's pot.
The leader is dragged down, the trailer jumps up, and it can backfire on both.

---

## 12. Prototype assumptions (to be confirmed by the designer)

The original draft left these open. Each is a guess to playtest, not a final rule.

| # | Topic | Prototype rule | Why |
|---|---|---|---|
| A1 | Objective dealing | Objectives dealt randomly, separate from characters | In the draft each character has a fixed objective; since characters are public, the "secret" would be known to everyone. Alternative: dealt matched to character (as written). |
| A2 | Number of rounds | Eliminate until 2 remain, then 1 Final Round with no elimination | The draft says "remaining players enter the final round" without a count. |
| A3 | Reshuffle | Everything reshuffled at round start; smuggled cards expire | Draft does not say if decks persist between rounds. |
| A4 | Round end | Also ends when all players CASHED OUT | Draft only says "when the Main Deck runs out", which would leave a stuck table. |
| A5 | Elimination tie | Sudden-death Point Card draw | Not covered. |
| A6 | Cashed-out targets | Can still be stolen from | Keeps interaction alive; CASH OUT is not a safe room. |
| A7 | Out-of-turn draws | Only Point/Negative/CRASH apply | Draft states this for Share the Risk; reused for THE BOSS. |
| A8 | Loan Shark | "Draw 2 more before CASH OUT" applies now, not next turn | As written, you could take +30 and CASH OUT, so the debt never comes. |
| A9 | Bodyguard | Lasts until used or round end | "Until your next turn" breaks if you cashed out. |
| A10 | Driver | Self-recipient clause removed | The clause was self-contradictory. As a pure "give away" card it is kingmaking; playtest whether it is fun or dead. |
| A11 | Gambler ability | Free DOUBLE once per round | As written ("draw again without choosing CASH OUT") it is identical to a normal PUSH and does nothing. |
| A12 | One More "X" | X = 3 | Draft left "X" blank. |
| A13 | 3-player objectives | Counts of 3 become 2 | Clean Exit needs 3 cash-outs but a 3p game has 2 rounds → impossible. |
| A14 | Share the Risk | Only players who haven't cashed out may share; sharer's score is replaced and they cash out | Draft unclear whether the sharer's half is added or replaces. "Added" is free points with no risk for the sharer. |

### Known design issues (not changed, just flagged for playtest)

- **SECOND DRAW ≈ FORCED PUSH:** both make you draw another card now. Consider making one different.
- **THE INSPECTOR is usually blank:** players rarely hold face-down cards. Idea for later: look at
  another player's Secret Objective.
- **Elimination = waiting:** eliminated players sit out the rest of the game. Watch how long they wait.
- **Round score resets:** only the current round matters for survival, so early rounds may feel low
  stakes except for objective progress.

---

## 13. TTS build requirements (for the building agent)

**Deliverable:** a TTS saved game (`.json` + card images) that loads with everything from §2 laid
out per §10, ready for a 3–5 player hotseat or online game.

1. **Cards:** text-only faces, no art (prototype). Each face shows: name (large), type line
   (POINT / NEGATIVE / CRASH / SPECIAL / NPC TRIGGER / NPC / CHARACTER / OBJECTIVE), effect text
   from this file verbatim, and the card ID small in a corner. Generate the faces with a script
   (e.g. Python + Pillow) into custom deck sheets.
2. **Card backs:** a different back per deck: Main Deck, NPC, Character, Objective. The 6 Reserve
   NPC Triggers use the **Main Deck back** (they get shuffled in).
3. **Colors on Main Deck faces:** Point = green, Negative = orange, CRASH = red, Special = blue,
   NPC Trigger = purple. Readable at table zoom.
4. **Score counters:** one per seat (TTS Counter object or equivalent), clamped at 0 if scripted.
5. **Round tracker:** printed board track 1–4 with "NPC Triggers: 6 / 8 / 10 / 12" under each step,
   plus a marker.
6. **Optional scripting (nice to have, not required):** a "New Round" button that gathers both
   decks, adds 2 Reserve NPC Triggers from Round 2 on, shuffles, and zeroes scores. Manual play
   must work without any script.
7. **Player aid card** with the §5 turn flow, shortened.
8. **Verify before handing back:** card counts per §6–§9 (Main 50 + 6 reserve, NPC 20, Character 5,
   Objective 5); every card text matches this file; the save loads with no missing images.
   Report any rule you could not implement or that felt contradictory.

---

## 14. Playtest questions (first sessions)

Prototype question: **is the PUSH / CASH OUT moment tense, and do NPCs make the later rounds more
exciting or just more random?**

After each game, every player answers alone:
1. What was the most exciting moment?
2. What was the most important decision you made?
3. Did your secret objective change how you played? Did you guess anyone else's?
4. Was there any moment the rules didn't cover?
5. If eliminated: how long did you wait, and was watching fun?
6. If you could change one thing, what would it be?

Track per game: total time, rounds played, who won / no winner, number of Share the Risk uses,
how often the Main Deck ran out vs. everyone cashed out.
