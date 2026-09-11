# Pravidlá pre prácu v tomto repozitári

## Odovzdávanie práce

Keď dokončíš zadanie, **pošli výsledok mailom na t.kucharcik@gmail.com**.
Nie len do chatu — mail chodí vždy.

Čo má v maili byť:

- Čo je hotové, jednou vetou navrchu.
- Vetva a odkaz do repozitára, kde to je.
- Odkazy na konkrétne súbory (pri PDF priamo na jednotlivé lekcie).
- Čo som musel overiť alebo čo vyšlo inak, než sa čakalo.
- Čo ostáva na Tomášovi.

Prílohy majú strop 25 MB, ale cez tento kanál sa base64 väčších súborov
neprenesie. Pri väčších výstupoch posielaj **odkazy na súbory v repozitári**,
nie prílohy.

## Fakty a zdroje

Platí `ZDROJE_A_FAKTY.md`: hype smie byť v hooku, fakty musia byť presné.

- Pohyblivý údaj (cena, názov plánu, dostupnosť modelu) = uveď dátum a zdroj.
- Keď si zdroje protirečia, nezaklincuj číslo. Napíš štruktúru a „over si v účte".
- Nikdy netvrď niečo, čo nemáš z primárneho zdroja.

## Jazyk a tón

Všetko po slovensky, aj kód a komentáre v generátoroch.

- Krátke vety. Žiadne prívlastky navyše.
- Priznané limity namiesto sľubov.
- Nepoužívať: revolučný, inovatívny, riešenie (v marketingovom zmysle).

## Kurz

`KURZ/` má vlastné `README.md` — formát obsahu aj postup generovania sú tam.
Upravuje sa `KURZ/obsah/*.txt`, potom `python3 KURZ/build/generuj.py`.
PDF a HTML sú generované výstupy, ručne ich neupravuj.
