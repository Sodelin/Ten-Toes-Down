# Bounded cast inventory for Books I-VI

This is a continuity and voice-design roster for chapter-by-chapter audiobook production, not a mass speaker assignment. It comes from the three existing source briefs, `analysis-1-2.md`, targeted name and heading searches, and selected local passages. It is not a claim to have read all six books word for word. The machine-readable record is `work/cast-inventory.json`.

## Lock these identities

- **AIDEN** — all six books; narrator and protagonist. Keep the selected local Qwen reference in `outputs/ten-toes-down-audio/voice-design/aiden-reference.wav` (manifest SHA-256 `a8ebab9b6728b86706c35fb2781ddef56d24514e37195066dcdb54382ca2222a`). Do not create a second voice for his quoted dialogue.
- **TANK** — all six books; Aiden's chosen brother and Rosa's partner/husband. Keep the selected deeper Qwen reference in `outputs/ten-toes-down-audio/voice-design/tank-reference.wav` (manifest SHA-256 `210f9dc804159ebd0ffe15b24dc28284c986bf632d09df03f5ed2814a1640d7b`).

These references are original synthetic identities, not celebrity clones. Regenerating VoiceDesign references would replace the identities even if the seeds stayed the same.

## Stable principal ensemble

| Speaker key | Books | Continuity role | Vocal contrast cue | Best compact evidence |
|---|---:|---|---|---|
| SHAWNA | I-VI | Aiden's wife; singer, navigator, planner, armed protector | Clear, controlled, direct; intimate with Aiden and steely in tactical lines | I.4:2481-2485 singing stops the room; II.11:5947-5949 runs the station rescue; III.8 operational route work; VI.15:6013-6037 fights Zero beside Aiden |
| ROSA | I-VI | Shawna's old friend and singer; Tank's partner/wife; crowd organizer | Seasoned, expressive warmth with command; more lived-in and earthy than Shawna | I.3:1687-1689 explicitly describes her voice; V.4:2339-2341 directs evacuation over gunfire; VI.22:9077-9081 vows |
| MERCEDES | I-VI | Friend, performer, driver, organizer, business owner with Porsche | Warm, socially expansive, quick, teasing | I.2:753-755 introduction; I.1:333-349 recovers her recordings and fights; III.24:9357-9359 makes Alina a real partner |
| PORSCHE | I-VI | Driver, rescuer, organizer, business owner with Mercedes | Firm attack, cooler focus, dry playfulness | I.2:895-897 introduction at the wheel; I.1:253-337 duplicate-case switch; IV.22:7568-7570 named on Velvet Mile papers |
| MARCELLUS | I-VI | Master jeweler, Blue Mercy's maker, crown authenticator, older adventurer | Older, deliberate, dry, exact; warmth emerges through craft and memory | I.6:3411-3413 “violent when disappointed”; IV.5:1818-1820 on possession; IV.21:7100-7104 studies workmanship; VI.24:10071-10075 teaches apprentices |

Mercedes and Porsche are established friends and business partners. The bounded pass did not establish that they are romantic partners, so the audiobook should not encode that assumption. Marcellus is repeatedly called an old man, but an exact present-day age was not confirmed.

## Recurring supporting identities worth preserving

| Speaker key | Books | Function | Contrast cue |
|---|---:|---|---|
| GLORIA_KNOX | I-IV, VI | Police chief and Aiden's institutional superior | Crisp, spare command with dry patience; I.3:1909-1912 gives age 53 and her sharp authority |
| DR_VEGA | I-II, IV, VI | Physician who enforces Aiden's bodily limits | Measured clinical precision and deadpan humor; I.3:1415-1435, IV.13, VI.23:9343-9347 |
| VICTOR | II-VI | Lightning rival turned friend and rescuer | Brighter, more formal and eager than Aiden; II.1:253-255, II.9:5327-5329, VI.20:8129-8333 |
| CASSIUS | III-IV, VI | Racing rival turned friend; Inez's partner; Nero's son | Controlled pride and dry elegance, emotion tightening in family scenes; III.3:1033-1043 |
| INEZ | III-IV, VI | Racer, Cassius's partner, Esteban's daughter and rescuer | Quick, candid competitive confidence; III.1:259-263, III.3:933-943 |
| ISOLDE | IV-VI | Dancer, vault-knowledge holder, Marcellus's recovered love | Mature poise, musical timing, firm instruction; IV.5:1656-1692 |
| VESPER | V-VI | Royal insider, dancer, historical witness and ally | Controlled elegance and careful phrasing, with sharp wit; V.4:2297-2299, V.19:8913-8955 |
| LIORA | VI | Berth manager, route expert and future First Dance operator | Explicitly clear and calm on radio, tighter under danger; VI.10:4329-4331 and 4511-4513 |

Liora is major inside Book VI rather than a six-book recurring character. The same distinction applies to many valuable regional characters: a stable voice across their own arc is useful, but they should not all occupy permanent ensemble slots.

## Major antagonist voices by arc

| Speaker key | Books | Aliases and function | Contrast cue |
|---|---:|---|---|
| RED | I | Red = Mr. Redmond/Redmond; Book I crime boss | Polished restraint and intimate menace; I.10:6038-6040 confirms the alias |
| VOSS | II | Chancellor Voss; academy chancellor and Heart/time-door conspirator | Cool institutional formality, without Knox's practical warmth; II.1:483-487 and II.7:3967-3969 |
| KELLER | II | Colonel Ernst Keller; Saint-Orage commander | Smooth amplified command turning cold; II.9:5385-5389 explicitly describes the voice |
| AURELIO | III | Duke Aurelio Cruel; coercive race patron | Cultivated, entitled calm that frays under defeat; III.3:1175-1179 gives age 48 and dangerous bearing |
| BELLARIO | III | Aurelio's announcer, official and fixer | Broadcast polish with coercion inside the rules; III.1:263-265 and III.3:1315-1319 |
| SOLOMON_SAINT | III-IV | General Solomon Saint; tournament architect and Book IV principal threat | Still, economical military authority; III.24:9483-9489 gives age 51 and explicit stillness |
| EMPEROR_ZERO | V-VI | Rafael Sorel = Emperor Zero; minister turned emperor | Smooth court control that hardens as recognition slips; V.6:3019-3025 confirms the identity |

Do not split Rafael Sorel and Emperor Zero into separate voices. Do not confuse Solomon Saint with the Saint nightclub or Red Saint Works.

## Limited and utility roles

- **BIG_T / T** is one confirmed person, a paternal criminal predecessor who shoots Aiden and dies early. Keep one voice through living scenes and memories, but he does not need a permanent six-book slot. Evidence: I.2:565-623; I.3:1387-1443.
- **TICKET** is the unnamed “ticket man” in the Book I funeral opening, not a recurring person. The pilot's dry service-counter reading fits I.1:51-55 and 507-509. The cited scene does not establish a personal name or pronoun.
- **GUEST** is a production pool for isolated unnamed lines, not a canonical identity. Do not let it absorb named characters or multiple speakers who converse with each other.
- Valentino and Silas Gold are named Book I antagonists and should sound distinct in their chapters, but their limited scope does not justify permanent ensemble priority.
- The unnamed woman at the bakery in VI.24 is memorable but appears in one scene. Do not turn “the baker” into a named, supernatural, or recurring office without source evidence.

## Chapter-pass queue

Delay exact casting until each relevant chapter is prepared:

- Book II: Dean Storm, Petra Stone, Bell, Pike, Dr. Ilya Reiss, Commander Sable, Finn Cinder.
- Books III-IV: Nero, Esteban, Lark, Celadon, Alina, Rafe Velluto, Odette, Graves. Nero and Esteban need separate older-father identities. The two characters called Mateo may be different people; do not merge them without a direct continuity check.
- Books V-VI: Bastien, Magnolia Saint-Clair, Noor Vale, Salma, Anton Atlas, Roland Ruin, Gideon, Orson, June, Adrian. Noor Vale is explicitly unrelated to Marcellus (VI.9:4055-4059).

For each chapter, extract only named dialogue turns and locally recurring unnamed roles, reconcile aliases against the JSON inventory, and then add a voice only when the chapter proves it needs one. That keeps publication token-efficient while preserving identities that matter.
