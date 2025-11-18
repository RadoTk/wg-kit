## Objectif
- Extraire et centraliser toutes les propriétés de typographie des pages `Conseil` et `Accueil` dans `static_src/scss/_font.scss`.
- Charger les familles de polices depuis Google Fonts (Montserrat, Oswald) avec `display=swap`.

## Chargement Google Fonts (recommandé)
- Charger UNE seule fois les polices via un stylesheet global (idéal pour éviter les doublons):
```
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&family=Oswald:wght@700&display=swap');
```
- Emplacement recommandé: la feuille d’entrée globale (ex: `static_src/scss/main.scss` ou l’entrée styles du projet) avant tout autre import.
- Si aucune entrée globale n’existe, placer temporairement l’`@import` en tête de `static_src/scss/_font.scss` et veiller à n’« utiliser » ce fichier qu’une seule fois côté bundle (sinon le CSS importé sera dupliqué).

## Inventaire des tokens à créer
- Familles: `Montserrat` (texte/labels), `Oswald` (titres).
- Tailles clés: 12, 14, 16, 20, 36, 43.
- Espacements de lettres: 0, 0.64, 0.80, 0.96, 1.12, 1.44.
- Poids: 400, 600, 700.
- Transformations: `uppercase` et `none`.

## `_font.scss` (variables + mixins)
```
$FONT_SANS: Montserrat, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", SimHei, Arial, Helvetica, sans-serif;
$FONT_HEADING: Oswald, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", SimHei, Arial, Helvetica, sans-serif;

$FONT_SIZES: (xs: 12px, sm: 14px, md: 16px, lg: 20px, xl: 36px, xxl: 43px);
$LETTER_SPACING: (none: 0, xs: 0.64px, sm: 0.80px, md: 0.96px, lg: 1.12px, xl: 1.44px);
$FONT_WEIGHTS: (regular: 400, semibold: 600, bold: 700);

@function sz($k) { @return map-get($FONT_SIZES, $k); }
@function ls($k) { @return map-get($LETTER_SPACING, $k); }
@function wt($k) { @return map-get($FONT_WEIGHTS, $k); }

@mixin textSans($sizeKey, $weightKey: regular, $lh: null, $lsKey: none, $transform: none) {
  font-family: $FONT_SANS; font-size: sz($sizeKey); font-weight: wt($weightKey);
  @if $lh != null { line-height: $lh; } letter-spacing: ls($lsKey);
  @if $transform != none { text-transform: $transform; }
}
@mixin textHeading($sizeKey, $weightKey: bold, $lh: null, $lsKey: none, $transform: uppercase) {
  font-family: $FONT_HEADING; font-size: sz($sizeKey); font-weight: wt($weightKey);
  @if $lh != null { line-height: $lh; } letter-spacing: ls($lsKey);
  @if $transform != none { text-transform: $transform; }
}
@mixin labelUpper($sizeKey, $weightKey: semibold, $lh: null, $lsKey: md) { @include textSans($sizeKey, $weightKey, $lh, $lsKey, uppercase); }
```

## Remplacements dans les modules SCSS
- Ajouter en haut:
```
@use '../../static_src/scss/font' as font; // depuis `.figma/44_3481` et `.figma/164_3208`
```
- Remplacer les propriétés typographiques par des mixins:
  - `.offreAbonnement`: `@include font.textSans(md, bold, 19px, none, uppercase);`
  - `.a20VieSurTousLesProd`: `@include font.textSans(md, semibold, 19px);`
  - `.chien` / `.quizzProduit` / `.conseils`: `@include font.labelUpper(sm, semibold, 17px);`
  - `.ouvrirUnCompte`: `@include font.labelUpper(sm, bold, 17px);`
  - `.chien3`: `@include font.labelUpper(xs, regular, 14px, md);`
  - Titres (`ARTICLE À LA UNE`, `TOUS LES ARTICLES`): `@include font.textHeading(xl, bold, 43px, xl, uppercase);`
  - `.titreDeLArticle`: `@include font.textSans(md, semibold, 21px);`
  - Paragraphes (`.loremIpsum...`): `@include font.textSans(md, regular, 21px);`
  - Dates (`.a081225`): `@include font.textSans(xs, regular, 16px, md);`
  - Boutons/CTA (`.lireLArticle`, `.sInscrirLaNewsletter`): variantes `labelUpper` adaptées.
  - Footer (`.infosPratiques`, `.recevezNosConseilsEt`, `.votreMail`, `.chien4`): variantes `textSans`/`labelUpper` avec ls 0.64–0.80 et lh 19–24.

## Vérification
- S’assurer que l’`@import` Google Fonts est chargé une seule fois (network tab). 
- Comparer avant/après: tailles, hauteurs de ligne, capitalisation et espacement des lettres inchangés.
- Tester `Conseil` + `Accueil` pour régressions visuelles sur titres, labels, paragraphes et CTA.

## Résultat
- Polices Google Fonts chargées proprement (`display=swap`).
- Typographie uniformisée via tokens et mixins.
- Maintenance simplifiée: une modification dans `_font.scss` se propage aux vues concernées.