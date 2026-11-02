# D15 review round 1 (POST HOC): lab notebook

Critique: `paper/Critic/round_1_D.txt` (item 2: reference-list length uncontrolled; item 3: reviews vs research articles). These analyses were designed after the outcomes had been seen and are labelled post hoc everywhere. They use the frozen scores (`d08_scores_20261101_01`, hashes verified at start) and the labels of `d08_eval`.

## d15_lenadj_20261101_01 (61 s)
- Reference-count deciles (candidates, main): edges 1–9, 9–16, 16–23, 23–29, 29–34, 34–41, 41–48, 48–58, 58–76, 76–4,180. Median references: exposed 51, unexposed 34.
- **MH OR S1 ≥ 1, strata journal × year × decile: 3.03 [2.76, 3.33]** (1,838 strata, 3,747 positives; journal × year alone 2.99). Paper-mill 4.12 [3.21, 5.29]; other 2.89 [2.61, 3.19].
- Share S2: positive rate 0 0.035%; (0, 1%] 0.065%; (1%, 2%] 0.21%; (2%, 5%] 0.44%; > 5% 0.50%. MH vs S2 = 0 within journal × year × decile: 1.74 [1.14, 2.66], 2.82 [2.33, 3.41], 2.98 [2.64, 3.35], 3.96 [3.24, 4.85].
- Reviews (PubMed D016454, D000078182, D017418): 1,253,585 candidates (11.9%). Share by S1 = 0, 1, 2, 3–4, 5+: 11.6%, 26.1%, 35.5%, 47.8%, 69.6%. Reviews retracted later: 0.030%, 0.049%, 0.012%, 0.068%, 0.099% (1/1,010). **Non-reviews: 0.036%, 0.35%, 0.79%, 1.52%, 2.27% (10/441).** MH without reviews 3.19 [2.90, 3.51].
- T0': MH with deciles 2.47 [2.28, 2.67] (journal × year alone 2.00); paper-mill 1.92; other 2.94; non-reviews 2.58.
- Reading: reference-list length does not explain the signal; the flat rate at S1 ≥ 5 in the main table is a review effect; among research articles the dose-response is monotone.

## d15_screen_20261102_01 (36 s): review round 2, POST HOC
Critique `paper/Critic/round_2_D.txt` (optional item): back the "set reviews aside" recommendation with a number. Same ranking rule as `d08_eval` (S1, then S2, then seeded tie-break after sorting by node ID); frozen scores verified.
- Main, all candidates (reproduces d08_eval): @1,000 9 hits (0.90% [0.47, 1.70], lift 21.9); @10,000 72 (0.72%).
- **Main, reviews excluded** (9,242,265 candidates, 3,939 positives, base 0.0426%): @100 1 (1.0%); **@1,000 22 hits (2.20% [1.46, 3.31], lift 51.6)**; @10,000 109 (1.09% [0.90, 1.31], lift 25.6).
- T0', reviews excluded: @1,000 24 (2.40% [1.62, 3.55], lift 31.7); @10,000 179 (1.79%). All candidates: @1,000 11 (1.10%).
- Wilson intervals (not bootstrap) for these post hoc precisions.
