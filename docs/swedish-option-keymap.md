# Svenska med Option på amerikansk layout

Implementerat och byggt 2026-09-09. Behåll **U.S.** som inmatningskälla i macOS.

| Tangent | Vanligt | Shift | Option | Shift + Option |
| --- | --- | --- | --- | --- |
| `\` | `\` | `\|` | å | Å |
| `;` | `;` | `:` | ö | Ö |
| `'` | `'` | `"` | ä | Ä |

Både vänster och höger Option/Shift stöds. Din vänstra tumknapp är redan Option.
Den gamla svenska toggle-knappen är nu obunden. Dess gamla lagerplats är ett
transparent, oanvänt lager så att keypad, Fn och Mod behåller sina nummer.

## Implementation

- `config/adv360.keymap` kopplar de tre tangenterna till de nya beteendena.
- `config/swedish.dtsi` innehåller Option-/Shift-val och svenska makron.
- `config/keymap.json` har synkats med de fem aktiva lagerplatserna. Det är en
  äldre GUI-representation; definitionerna i `swedish.dtsi` måste också bevaras
  vid redigering. JSON-filen ensam beskriver inte de egna beteendena.

Option+A ger å; Option+U följt av A/O ger ä/ö. För Ä/Ö får bara det sista
bokstavstrycket Shift. Varje makrosteg maskerar fysiskt hållna Option/Shift och
använder explicita keycode-kombinationer för de modifierare som faktiskt ska
skickas. Därmed försvinner inte Option-maskningen när ett nästlat mod-morph
sätter en annan mask. Makrona har noll väntetid och tapptid, och maskeringen
sker inuti de köade stegen.

## Firmwarebedömning

Ingen ny firmwarebas behövs för funktionen. Repots `config/west.yml` använder
`refil/zmk`, gren `adv360-z3.5-2`, samma referens som Kinesis ordinarie V3.0-gren
vid kontrollen. Uppströms konfigurationsrepo kontrollerades vid `97f5d73`;
nyare ändringar där gäller bland annat dokumentation och byggcache.

Detta är en bedömning av repot, inte en avläsning av tangentbordets installerade
version. I repots mappning skriver **Mod+V** versionsmakrot i ett tomt textfält.
Om tangentbordet kör en annan mappning kan genvägen skilja sig.

Den nya keymapen kräver att den nybyggda firmwarefilen installeras. För en
äldre version före februari 2025 rekommenderar Kinesis också uppdatering för
bland annat förbättrad synkning och minskat tangentstuds.

Källor: [Kinesis firmwaremanifest](https://github.com/KinesisCorporation/Adv360-Pro-ZMK/blob/V3.0/config/west.yml),
[Kinesis support](https://kinesis-ergo.com/support/kb360pro/),
[mod-morph i den använda firmwaregrenen](https://github.com/ReFil/zmk/blob/adv360-z3.5-2/app/src/behaviors/behavior_mod_morph.c),
[modifierarhanteringen](https://github.com/ReFil/zmk/blob/adv360-z3.5-2/app/src/hid.c).

## Färdigbyggda filer

| Användning | Vänster halva | Höger halva |
| --- | --- | --- |
| Keymap från detta repo, utan Clique | `firmware/swedish-left.uf2` | `firmware/swedish-right.uf2` |
| Med stöd för Clique/Studio | `firmware/swedish-left-clique.uf2` | `firmware/swedish-right.uf2` |

Välj en vänsterfil. Högerfilen används i båda fallen. Filerna ligger lokalt och
ignoreras av Git enligt repots befintliga inställning.

Byggd ZMK-revision: `d93499bb877f2711989e6cbbe1feed9e9a792ca3`.
Keymapens byggidentifierare: `9d51af4` (hash av `adv360.keymap` + `swedish.dtsi`).

### Installera

Följ [Kinesis installationsanvisningar](https://github.com/KinesisCorporation/Adv360-Pro-ZMK#flashing-firmware):

1. Anslut vänster halva med USB och sätt den i bootloaderläge med Mod + dess
   bootloaderknapp, eller den fysiska resetknappen enligt manualen.
2. Kopiera vald vänsterfil till USB-enheten som visas. Den kopplas bort när
   filen har installerats.
3. Stäng av båda halvorna, starta vänster, anslut sedan höger med USB och sätt
   höger i bootloaderläge. Kopiera högerfilen till dess USB-enhet.
4. Koppla ur och starta höger halva igen. Kontrollera U.S. i macOS och prova
   `åäö ÅÄÖ` samt exempelvis `const city = "Växjö";`.

Om du har sparat en layout i Clique/Studio och använder Clique-varianten kan
den sparade layouten ta över den nybyggda. ZMK beskriver då åtgärden
**Restore Stock Settings** i Studio för att använda keymapen från firmware.
Det ersätter sparade layoutändringar; dokumentera sådana först om de ska
behållas. [ZMK Studio – Keymap Changes](https://zmk.dev/docs/features/studio#keymap-changes).

Användaren har installerat firmware och bekräftat att tangentbordet och de svenska
kombinationerna fungerar. Ingen återställning har utförts av agenten.

## Verifiering

- ZMK:s riktiga `native_posix_64`-simulator: **136 förväntade HID-tangenttryck**
  passerade. Testet omfattar US-symboler, alla sex svenska bokstäver,
  vänster/höger/korsade modifierare, upprepning med Option hållen samt att
  Option släpps före bokstavstangenten.
- Mappningen av de fysiska tangenterna, lagerindex och JSON-synkningen kontrolleras.
- Vänster, höger och vänster med Clique har alla kompilerats framgångsrikt.
- Användaren har även bekräftat funktion på det fysiska tangentbordet i macOS.
- Option + `\` öppnade också Claude-overlayen. Användaren har stängt av
  den funktionen i Claude; någon ytterligare firmwareändring gjordes inte.

Reproducerbart integrationstest finns i `tests/swedish.py`, med köranvisningar
överst i filen. Firmware kan även byggas med repots vanliga byggflöde.
