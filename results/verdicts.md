# Operational verdicts

As-of: 2026-06-17T07:45:00+05:30

Each row covers the evaluated trips named in its note. Numbers describe historical progress-time deficit, not a guaranteed arrival ETA. Bookings are not confirmed waiting riders. No external actions were executed.

| route | verdict | note |
| --- | --- | --- |
| 9 | HOLD | Both references below materiality across all three observations. Scope: TRIP_013/V-11. |
| 11 | CALL_DRIVER | Direct verification takes precedence: Persistent origin-bound telemetry after departure; verify bus location and tracker assignment. Scope: TRIP_014/V-06. |
| 12 | PUSH_LATE 9 min | Both references at/above materiality across all three observations; rounded only after eligibility. Scope: TRIP_015/V-10. Operational evidence governs this row. HANDOFF.md rev. C requests contractual lateness=0; override not applied. |
| 14 | CALL_DRIVER | Direct verification takes precedence: Usable telemetry absent for more than five minutes; verify current service/location; completion is unconfirmed. Scope: TRIP_016/V-04. |
| 17 | CALL_DRIVER | Direct verification takes precedence: Usable telemetry absent for more than five minutes; verify current service/location; completion is unconfirmed. Scope: TRIP_017/V-05. 6 booking/promise warnings require separate ops/product reconciliation; HOLD does not certify promises. |
| 21 | HOLD | Both references below materiality across all three observations. Scope: TRIP_018/V-03. 6 bookings outside assessment on configured excluded trips: TRIP_019/V-09. 6 booking/promise warnings require separate ops/product reconciliation; HOLD does not certify promises. |

# Calculation evidence

## Route 9

### TRIP_013 / V-11

State: fresh_credible; numerical eligible: True. Both references below materiality across all three observations.

Included bookings: 12; distinct rider IDs: 12. Promise warnings: 0. Invalid booking fields: 0.

| ping | source line | device time | receipt time | event age s | progress km | reference deficits min | median min | timetable min |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P-0003262 | 3263 | 2026-06-17T07:43:57+05:30 | 2026-06-17T07:44:00+05:30 | 63.000000 | 13.117091 | {"2026-06-15": -1.3766398933661677, "2026-06-16": -0.7053341480041837} | -1.040987 | 0.344793 |
| P-0003263 | 3264 | 2026-06-17T07:44:19+05:30 | 2026-06-17T07:44:21+05:30 | 41.000000 | 13.211017 | {"2026-06-15": -1.3546954978426982, "2026-06-16": -0.7387252721137685} | -1.046710 | 0.327615 |
| P-0003264 | 3265 | 2026-06-17T07:44:42+05:30 | 2026-06-17T07:44:44+05:30 | 18.000000 | 13.292535 | {"2026-06-15": -1.300454220249982, "2026-06-16": -0.6898439524889639} | -0.995149 | 0.377813 |

Unrounded reference brackets, raw source provenance, quality audit and position sensitivity are in evidence.json.

## Route 11

### TRIP_014 / V-06

State: origin_bound; numerical eligible: False. Persistent origin-bound telemetry after departure; verify bus location and tracker assignment.

Included bookings: 8; distinct rider IDs: 8. Promise warnings: 0. Invalid booking fields: 0.

| ping | source line | device time | receipt time | event age s | progress km | reference deficits min | median min | timetable min |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P-0003516 | 3517 | 2026-06-17T07:44:10+05:30 | 2026-06-17T07:44:11+05:30 | 50.000000 | 0.009634 | null | N/A | N/A |
| P-0003517 | 3518 | 2026-06-17T07:44:31+05:30 | 2026-06-17T07:44:35+05:30 | 29.000000 | 0.000000 | null | N/A | N/A |
| P-0003518 | 3519 | 2026-06-17T07:44:51+05:30 | 2026-06-17T07:44:54+05:30 | 9.000000 | 0.013278 | null | N/A | N/A |

Unrounded reference brackets, raw source provenance, quality audit and position sensitivity are in evidence.json.

## Route 12

### TRIP_015 / V-10

State: fresh_credible; numerical eligible: True. Both references at/above materiality across all three observations; rounded only after eligibility.

Included bookings: 9; distinct rider IDs: 9. Promise warnings: 0. Invalid booking fields: 0.

| ping | source line | device time | receipt time | event age s | progress km | reference deficits min | median min | timetable min |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P-0003622 | 3623 | 2026-06-17T07:44:12+05:30 | 2026-06-17T07:44:16+05:30 | 48.000000 | 5.562324 | {"2026-06-15": 8.801894967919093, "2026-06-16": 9.104474885981702} | 8.953185 | 9.958036 |
| P-0003623 | 3624 | 2026-06-17T07:44:31+05:30 | 2026-06-17T07:44:33+05:30 | 29.000000 | 5.620097 | {"2026-06-15": 8.86490522902233, "2026-06-16": 9.121797500716337} | 8.993351 | 9.970978 |
| P-0003624 | 3625 | 2026-06-17T07:44:51+05:30 | 2026-06-17T07:44:53+05:30 | 9.000000 | 5.671299 | {"2026-06-15": 8.928876281622859, "2026-06-16": 9.180711030624302} | 9.054794 | 10.035137 |

Unrounded reference brackets, raw source provenance, quality audit and position sensitivity are in evidence.json.

## Route 14

### TRIP_016 / V-04

State: stale; numerical eligible: False. Usable telemetry absent for more than five minutes; verify current service/location; completion is unconfirmed.

Included bookings: 12; distinct rider IDs: 12. Promise warnings: 0. Invalid booking fields: 0.

| ping | source line | device time | receipt time | event age s | progress km | reference deficits min | median min | timetable min |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P-0003826 | 3827 | 2026-06-17T06:56:13+05:30 | 2026-06-17T06:56:16+05:30 | 2927.000000 | 4.836196 | null | N/A | N/A |
| P-0003827 | 3828 | 2026-06-17T06:56:36+05:30 | 2026-06-17T06:56:38+05:30 | 2904.000000 | 4.961271 | null | N/A | N/A |
| P-0003828 | 3829 | 2026-06-17T06:56:54+05:30 | 2026-06-17T06:56:57+05:30 | 2886.000000 | 5.044372 | null | N/A | N/A |

Unrounded reference brackets, raw source provenance, quality audit and position sensitivity are in evidence.json.

## Route 17

### TRIP_017 / V-05

State: stale; numerical eligible: False. Usable telemetry absent for more than five minutes; verify current service/location; completion is unconfirmed.

Included bookings: 16; distinct rider IDs: 16. Promise warnings: 6. Invalid booking fields: 0.

| ping | source line | device time | receipt time | event age s | progress km | reference deficits min | median min | timetable min |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P-0004085 | 4086 | 2026-06-17T07:27:04+05:30 | 2026-06-17T07:27:07+05:30 | 1076.000000 | 14.552244 | null | N/A | N/A |
| P-0004086 | 4087 | 2026-06-17T07:27:22+05:30 | 2026-06-17T07:27:25+05:30 | 1058.000000 | 14.569459 | null | N/A | N/A |
| P-0004087 | 4088 | 2026-06-17T07:27:40+05:30 | 2026-06-17T07:27:42+05:30 | 1040.000000 | 14.569440 | null | N/A | N/A |

Unrounded reference brackets, raw source provenance, quality audit and position sensitivity are in evidence.json.

## Route 21

### TRIP_018 / V-03

State: fresh_credible; numerical eligible: True. Both references below materiality across all three observations.

Included bookings: 6; distinct rider IDs: 6. Promise warnings: 6. Invalid booking fields: 0.

| ping | source line | device time | receipt time | event age s | progress km | reference deficits min | median min | timetable min |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P-0004160 | 4161 | 2026-06-17T07:44:15+05:30 | 2026-06-17T07:44:17+05:30 | 45.000000 | 2.958280 | {"2026-06-15": -1.5877414159395684, "2026-06-16": 0.5223204066596701} | -0.532711 | -0.214493 |
| P-0004161 | 4162 | 2026-06-17T07:44:33+05:30 | 2026-06-17T07:44:34+05:30 | 27.000000 | 2.991010 | {"2026-06-15": -1.69193979132492, "2026-06-16": 0.6004442284014289} | -0.545748 | -0.185168 |
| P-0004162 | 4163 | 2026-06-17T07:44:51+05:30 | 2026-06-17T07:44:52+05:30 | 9.000000 | 3.039050 | {"2026-06-15": -1.7792086093526294, "2026-06-16": 0.4634702274796183} | -0.657869 | -0.282444 |

Unrounded reference brackets, raw source provenance, quality audit and position sensitivity are in evidence.json.

