# US för programmering och svenska bokstäver på Advantage360 Pro

> Historisk research före implementationen. Det valda Option-upplägget är nu implementerat; se [aktuell keymap och installation](swedish-option-keymap.md).

Undersökt 2026-09-09. Lokal utgångspunkt: `f48eb51` (2025-03-25), [gustavlrsn/Adv360-Pro-ZMK](https://github.com/gustavlrsn/Adv360-Pro-ZMK). Detta är research och förslag; ingen firmware har ändrats eller hårdvarutestats.

## Nuvarande lösning och orsaken till citatproblemet

[config/adv360.keymap](../config/adv360.keymap) innehåller följande lager: Base (0), swe (1), Kp (2), Fn (3) och Mod (4). Base använder `&tog 1` för att låsa/låsa upp svenska. Svenska ändrar bara tre positioner:

| Position i Base | Svensklagret | Aktivt makro |
| --- | --- | --- |
| `BSLH`, till höger om P | å | `swe_aa_2`: Option+A |
| `SEMI`, till höger om L | ö | `swe_oe_2`: Option+U, sedan O |
| `SQT`, till höger om föregående | ä | `swe_ae_2`: Option+U, sedan A |

Både vänster och höger keymap inkluderar `adv360.keymap`, som därför är källan för analysen. `config/keymap.json` är inaktuell och saknar svenska lagret; den behöver synkas innan GUI-flödet används.

Det är redan en US-layout med svenska tillägg, snarare än en komplett svensk layout. De äldre makrona utan `_2` finns kvar men används inte av svenska lagret. macOS-inställningen `AppleSelectedInputSources` visade U.S. vid undersökningen.

Fn nås med `&mo 3` på båda nedersta ytterpositionerna. Fn har `&trans` på samtliga tre positioner ovan. Transparens går vidare till nästa aktiva lägre lager, inte automatiskt till Base. När swe är påslaget kommer Fn därför fortfarande åt svenska makron där. Lagerordning och samtidiga aktiva lager beskrivs i [ZMK:s lagerdokumentation](https://zmk.dev/docs/keymaps/behaviors/layers).

## Rekommenderad första förbättring

Ge Fn explicita `&kp BSLH`, `&kp SEMI` och `&kp SQT` på samma tre positioner som i Base. Då kan svenska vara påslaget medan Fn tillfälligt ger programmeringstecknen:

| Svensk position | Fn + tangenten | Fn + Shift + tangenten |
| --- | --- | --- |
| å | `\` | `\|` |
| ö | `;` | `:` |
| ä | `'` | `"` |

Tabellen förutsätter U.S. och vanliga Shift-knapparna: Fn blockerar de två extra Shift-positionerna med `&none`. Ändra dem till `&trans` om även de ska fungera med Fn. Det konkreta problemet löses med tre bindningsändringar, utan att flytta svenska bokstäver eller införa ett nytt låst läge. Framför allt blir Fn+Shift+ä ett sätt att skriva dubbelt citattecken medan swe fortfarande är aktivt.

Nästa ergonomiska steg är en extra momentär Fn-knapp på en bekväm vänstertumposition: vänster tumme aktiverar symboler och höger hand skriver dem. Välj position efter vilka tumfunktioner användaren behöver. Detta är ett designförslag, inte bevisad ergonomisk överlägsenhet.

## Alternativ och vad andra har gjort

### Ett tydligare symbollager

Ett eget momentärt lager kan samla apostrof, dubbelt citattecken, backtick och parenteser på lättåtkomliga positioner. Det behöver ligga ovanför swe och ange explicita symbolbindningar. Den svenska programmeraren bakom [lydell/keyboard](https://github.com/lydell/keyboard) beskriver just ett separat symbollager, med de tre citatliknande tecknen samlade. Hen vill att enkla och dubbla citattecken ska vara lika lättåtkomliga. Ergodox-versionen kombinerar firmware med nästan vanlig svensk OS-layout. Detta är ett konkret personligt exempel, inte belägg för att upplägget är vanligast.

### US som standard och svenska bara medan tummen hålls

Med en momentär svensk knapp blir vanliga tryck alltid US och tumme+å/ä/ö-positionen svenska. Man slipper minnas ett låst läge. Det passar särskilt blandad kod och korta svenska inslag; längre svenska texter kan innebära fler tumtryck. ZMK:s `&mo` aktiverar och avaktiverar lagret direkt vid tryck respektive släpp. `&sl` är ett alternativ för ett enstaka efterföljande tecken. Se [lagerbeteenden](https://zmk.dev/docs/keymaps/behaviors/layers) och [sticky layer](https://zmk.dev/docs/keymaps/behaviors/sticky-layer).

Kombinationen `&tog 1` och `&mo 1` måste kontrolleras mot firmwareversionen. Nyare ZMK dokumenterar layer locking som bevarar ett låst lager vid momentärt släpp; repot använder den äldre forken `adv360-z3.5-2`, så samma beteende får inte förutsättas utan källkontroll eller test. Ett separat symbollager ovanför swe undviker den versionsfrågan.

### Andra sätt att nå svenska

[Hold-tap/layer-tap](https://zmk.dev/docs/keymaps/behaviors/hold-tap) kan kombinera Space vid kort tryck med lager vid håll, men kräver timing som passar skrivstilen. Prova helst en dedikerad lagerknapp först.

[Combos](https://zmk.dev/docs/keymaps/combos) ger ett tecken när två tangenter trycks nästan samtidigt. De behåller US-layouten men behöver provas mot vanliga bokstavsföljder och tangentbordets välvda yta. [Mod-morph](https://zmk.dev/docs/keymaps/behaviors/mod-morph) kan i stället välja svenska bara med exempelvis höger Option. Det kräver kontroll av modifierade genvägar och versaler. Dessa är möjliga alternativ, inte hårdvarutestade rekommendationer.

## Ska OS-inmatningsspråket växlas?

För den här konfigurationen rekommenderas en fast U.S.-inmatningskälla och förbättrad åtkomst i firmware. Svenska makron använder redan Macens Option-/accentmekanism. [Apple beskriver dead-key-sekvenser och Keyboard Viewer](https://support.apple.com/en-mide/guide/mac-help/mh27474/mac), där kombinationerna för den valda inmatningskällan kan kontrolleras. Tangentbordets lager och datorns inmatningskälla är två separata saker: firmware skickar knapptryck som datorn tolkar. Att byta OS till svenska utan att anpassa keymapen ändrar därför också programmeringstecknens resultat.

Det går att bygga en visuellt US-liknande firmwarelayout mot en fast svensk OS-layout. Språkalias och makron kan då skicka motsvarande svenska keycodes, men det är en större omarbetning. [ZMK Locale Generator](https://github.com/joelspadin/zmk-locale-generator) genererar sådana språkheaders från CLDR. [QMK:s officiella beskrivning av samma keycode-princip](https://docs.qmk.fm/reference_keymap_extras) förklarar uttryckligen att språkalias måste matchas av OS-layouten; de byter inte själva språk på datorn.

## Praktisk kontroll före användning

Efter en eventuell implementation bör följande provas på det verkliga tangentbordet:

- Med swe på och av: `'`, `"`, `;`, `:`, `\` och `|` via Fn.
- Svenska åäö och ÅÄÖ, särskilt Shift under de befintliga accentmakrona.
- Blandad text, exempelvis `const city = "Växjö";`, med svenska fortfarande påslaget.
- Att Fn-släpp lämnar swe i samma låsta tillstånd som före Fn-trycket.
- Relevanta genvägar och faktisk komfort vid tumme+Shift+högerhand.

Ingen sådan hårdvaruverifiering har gjorts i denna undersökning. Befintliga makron är Mac/U.S.-beroende; byte till Windows, Linux eller en annan inmatningskälla behöver separat kontroll.
