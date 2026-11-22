# news-image-20261122

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/Nugroho281/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/Nugroho281/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A one-page newspaper front page that sums up the world news of **Sunday 22 November 2026** in a single 1024×1024 image: 43 stories — 16 drawn as picture panels, 27 more in brief — under one giant date line. The hero story is the Russian drone strike that partly destroyed an apartment block near Kyiv, leaving at least 14 people missing. The pictured panels cover COP31 running into a second day of overtime in Antalya, the capture of FBI most-wanted cartel boss "El Chapo Isidro" in Mexico, the EU–Indonesia IEU-CEPA trade deal signed in Brussels, Iran's strike on Bahrain and the tankers hit in Hormuz, the Kryvyi Rih missile strike and the Russian cargo ship burning off Finland, the AI sell-off that pushed US stocks into correction, the Cikande candy-factory fire in Banten, the Indonesian police chief's rotation of 704 officers, BepiColombo entering Mercury orbit, Peru's magnitude 6.7 earthquake, South Korea's education minister resigning over an AI cheating scandal, Leeds stunning Chelsea 4–1, Alcaraz facing Zverev in the ATP Finals final, GTA VI's $3.8bn launch day, and the fire that gutted 32 homes in a Baduy village in Lebak.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=scz7tdtw&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards</sub>

## How it is made

`main.py` is a pure Python 3 standard-library program — no Pillow, no
numpy, no network. It draws the whole page at 2048×2048 (2×
supersample) with flat saturated shapes and a hand-built 5×7 pixel
font, then box-downscales to 1024×1024 so every letter and edge stays
sharp and the colours stay vivid. It writes `entry.png` (52 KB, well
under the 1 MiB gate) in about two seconds, deterministically: two
runs produce byte-identical output. The `entry.png` committed in this
repository is the program's exact output.

## Story credits — all reported on Sunday 22 November 2026

Pictured (16):

- Kyiv apartment block hit by a Russian drone strike, at least 14
  missing — One Turn day page (BBC / Al Jazeera wires), 22 Nov.
- COP31 in Antalya enters a second day of overtime; fossil-fuel row;
  $120bn adaptation target dropped — One Turn (Straits Times,
  Tagesschau, RFI).
- Mexico captures Fausto Isidro Meza Flores, "El Chapo Isidro", in
  Guasave, Sinaloa; 11 killed — Al Jazeera, BBC News, PBS NewsHour;
  TFI News day page.
- EU and Indonesia sign the IEU-CEPA trade deal in Brussels; 98.5% of
  tariffs removed after ten years of talks — Cutthroat News world
  digest; suratNET, 22 Nov edition.
- Iran strikes a Bahrain industrial site; two tankers struck in
  Hormuz; US naval blockade day 130 — France 24, Middle East Eye,
  The Hindu via One Turn.
- Russian missiles hit Kryvyi Rih (2 dead, dozens hurt); a Russian
  cargo ship burns off Finland after a drone attack — Al Jazeera,
  BBC News, UPI via One Turn.
- AI sell-off: S&P 500 −3.7% to 6,910, into correction; Nikkei −5.06%
  — CNBC, BBC via One Turn.
- Fire at the PT Fonusa Agung Mulia candy factory in Cikande, Serang:
  3 bodies found, 36 people still sought — Kabarindo; Kita Indonesia
  Satu, 22 Nov.
- National police chief Suyudi Ario Seto rotates 704 personnel; 12
  regional police chiefs replaced — Kita Indonesia Satu; Poskota,
  22 Nov.
- BepiColombo enters orbit around Mercury after an eight-year
  journey — One Turn day summary, 22 Nov.
- Magnitude 6.7 earthquake shakes Peru's Andes — TFI News day page,
  22 Nov.
- South Korea's education minister Choi Kyo-jin resigns over an AI
  exam-cheating scandal — BBC News, The Guardian, SCMP via One Turn.
- Leeds United stun Chelsea 4–1 at Stamford Bridge, first win there
  since 1999, Okafor scoring twice — Sky Sports via iqmia; Cutthroat
  News.
- Alcaraz beats Shelton 3–6 6–3 7–6 and Zverev beats Medvedev to set
  up the ATP Finals title match in Turin — ATP / Reuters wires (ANI,
  IANS, DevDiscourse), 22 Nov.
- GTA VI takes a record $3.79bn on launch day — iqmia world news
  summary, 22 Nov.
- Fire destroys 32 homes in a Baduy village in Lebak, Banten; 132
  people displaced — Kita Indonesia Satu; Kabarindo, 22 Nov.

In brief (27): Hegseth's secret memo restricting the US–Canada
defence relationship and the Depok courier killed by floodwater
(TFI News; Kita Indonesia Satu) · Estonia closing its Russian
border and Russian missiles landing in Poland (TFI News) · Denmark
expelling a Russian attaché and the Rohingya welcoming the UN
court's genocide verdict (One Turn) · the UAE shuttling oil past
Iran through Hormuz and the Houthis striking Saudi Arabia (TFI
News; iqmia) · a Gaza aid vehicle hit and the UK–EU deals signed in
London (One Turn; Cutthroat News) · the FBI NCIC database breach
and Amazon's near-$7.5bn deal for AI startup Decart (CNBC and Crypto
Briefing via iqmia) · IBM's 520-qubit Nighthawk r3 (iqmia) · the
Bayelsa mourners' boat capsize killing at least 24 in Nigeria and
Bolsonaro in intensive care (Cutthroat News; One Turn) · France's
sixth Saturday of protests, 82,500 marching (Cutthroat News) ·
Nepal PM Balendra Shah's India visit and India–China corps
commander talks on the Arunachal frontier (Dainik Jagran) · India
declaring at 720/9 against New Zealand for a 352-run lead (Dainik
Jagran) · James Harden's 51 points passing Kobe Bryant, England
thrashing the All Blacks at Twickenham, Messi's second straight
MLS Golden Boot as Miami lose 0–3, Márquez crashing in the Portugal
MotoGP sprint as Bezzecchi wins (One Turn sports; Kita Indonesia
Satu) · Indonesia U-17 drawing Myanmar 2–2 and Gunung Ibu erupting
with a 400 m ash column (Nusantara Jaya News; Kita Indonesia Satu)
· Megawati's PDIP staying outside the government (suratNET) · the
Indonesian Navy foiling a 10 kg drug run from Malaysia off Batubara
(Kita Indonesia Satu).

## License

MIT — see `LICENSE`.
