# UTF-8 Text Converter

Convertisseur graphique pour textes et sous-titres qui :
- détecte l’encodage, convertit en UTF-8 et corrige éventuellement le texte (mojibake) ;
- détecte automatiquement la langue des fichiers `.srt` et ajoute un suffixe type MKVToolNix (`-heb`, `-eng`, `-ger`, etc.) aux fichiers convertis ;
- gère le drag & drop des fichiers dans l’interface ;
- permet de forcer l’encodage d’entrée, de choisir un dossier de sortie, de créer des sauvegardes `.bak` et de suivre la progression via une barre et un journal.

---

## 1. Fonctionnalités principales

- **Supports** : `.txt`, `.srt`, `.ass`, `.vtt`, `.md`, `.csv`, etc.
- **Interface Windows** (Tkinter + ttk) avec icône personnalisable.
- **Auto-détection** de l’encodage (via `chardet`) et conversion en UTF-8.
- **Corrections automatiques** (optionnelles) avec `ftfy`.
- **Langue** détectée via `langdetect` avec renommage automatique des `.srt` (`nom-heb.srt`, `nom-eng.srt`, …) en s'appuyant sur `language_suffixes.json`.
- **Drag & Drop** (via `tkinterdnd2`).
- **Traitement par lots** et conversion non bloquante (thread séparé).
- **Sauvegardes optionnelles** des fichiers d’origine.
- **Journal** des opérations et barre de progression.

---

## 2. Installation & configuration (poste développeur)

1. Installer Python (3.11+ recommandé).
2. Installer les dépendances :
   ```powershell
   pip install chardet ftfy langdetect tkinterdnd2 pyinstaller

   # Optionnel mais recommandé pour des suffixes langue ISO-639-2 complets
   pip install pycountry
   ```
3. Placer les fichiers suivants dans un dossier (ex. `C:\Dev\UTF8Converter`) :
   - `utf8_converter_gui.py`
   - `utf8converter.ico` (facultatif)
   - `README.md` (facultatif)

---

## 3. Exécution du script en mode développement

```powershell
python utf8_converter_gui.py
```

> Lance l’application avec tous les réglages (drag & drop, détection de langue, etc.).

---

## 4. Reconstruction de l’exécutable après chaque modification

1. **Ouvrir PowerShell** dans le dossier du projet (`C:\Dev\UTF8Converter`).
2. **Mettre à jour le script** (`utf8_converter_gui.py`).
3. **Reconstituer l’exécutable** avec PyInstaller :

   ```powershell
   pyinstaller `
       --noconsole `
       --onefile `
       --icon utf8converter.ico `
       --add-data "C:\Users\<VOUS>\AppData\Local\Programs\Python\Python3xx\Lib\site-packages\tkinterdnd2;tkinterdnd2" `
       utf8_converter_gui.py
   ```

   - Remplacez `C:\Users\<VOUS>\...` par le chemin réel de votre installation (`site-packages`).
   - Si vous n’avez pas d’icône, supprimez `--icon ...`.
   - Si vous préférez un dossier plutôt qu’un EXE unique, remplacez `--onefile` par `--onedir`.

4. **Récupérer l’exécutable** dans le dossier `dist/`.  
   - Exemple : `dist/utf8_converter_gui.exe`.

5. **Tester** l’EXE sur votre poste puis sur un poste sans Python.

### Remarque — Automatiser la reconstruction

Créez un script `build.ps1` contenant la commande ci-dessus. Ensuite, lancez simplement :

```powershell
.\build.ps1
```

à chaque fois que vous avez modifié le code.

---

## 5. Signature de l’exécutable (facultatif mais recommandé)

1. Obtenir un certificat de signature de code (OV ou EV).
2. Installer le Windows SDK pour disposer de `signtool.exe`.
3. Signer l’EXE :
   ```powershell
   signtool sign `
       /f "C:\Chemin\vers\certificat.pfx" `
       /p "mot_de_passe" `
       /tr http://timestamp.digicert.com `
       /td sha256 `
       /fd sha256 `
       dist\utf8_converter_gui.exe
   ```
4. Vérifier :
   ```powershell
   signtool verify /pa /v dist\utf8_converter_gui.exe
   ```

---

## 6. Distribution

- Copier `dist\utf8_converter_gui.exe` (et éventuellement `README.md`, `LICENSE`, ...) sur le poste cible.
- Si vous utilisez `--onedir`, copier tout le dossier `dist\utf8_converter_gui\`.
- (Optionnel) Emballer l’exécutable dans un installateur (Inno Setup, NSIS, etc.).
- Expliquer aux utilisateurs de cliquer sur “Informations complémentaires” puis “Exécuter quand même” si SmartScreen apparaît (sauf si vous avez une signature EV reconnue).

---

## 7. Dépannage rapide

| Problème | Solution |
|----------|----------|
| “Script file '^' does not exist” | En PowerShell, utilisez la backtick ``` ` ``` pour les lignes multiples, pas `^`. |
| Drag & drop ne fonctionne pas | Vérifiez que `tkinterdnd2` est bien installé et embarqué (`--add-data`). |
| Langue non détectée | Fichier trop court ou langue non reconnue ; le suffixe n’est pas ajouté. |
| EXE lourd / lent au démarrage | Essayez `--onedir` ou compressez avec UPX (`--upx-dir`). |

---

## 8. Personnalisation

- Les suffixes de langue sont compatibles style MKVToolNix (codes ISO-639-2/B quand disponibles) avec fallback automatique.
- Vous pouvez personnaliser les suffixes dans `language_suffixes.json` (prioritaire). Le script garde un fallback automatique si un code n'est pas trouvé.
- Adaptez la liste des encodages proposés (`ENCODINGS`).
- Modifiez les extensions prises en charge (`SUPPORTED_EXTENSIONS`).
- Ajoutez d’autres fonctionnalités (ex. mémorisation des réglages, previews, etc.).

---

## 9. Mise à jour automatique (popup au démarrage)

Le projet utilise une stratégie production : **GitHub Releases** comme source unique des mises à jour.

Fonctionnement :

- vérification asynchrone au démarrage ;
- popup avec **Update**, **Remind me later**, **Skip this version** ;
- téléchargement de la nouvelle version depuis l'asset `.exe` de la release ;
- remplacement de l'EXE via un script externe Windows (l'EXE en cours ne peut pas s'auto-remplacer pendant son exécution).

### Activation

1. Garder `ONE_CLICK_UPDATE_CONFIG = True` dans `updater.py`.
2. Créer `update_config.json` (à partir de `update_config.sample.json`) :

```json
{
   "github_repository": "eroisman/UTF8Converter",
   "asset_name": "utf8_converter_gui.exe",
   "github_token": ""
}
```

3. Token optionnel mais recommandé si vous voyez des erreurs 403.
4. Méthode la plus sûre : variable d'environnement locale `UTF8CONVERTER_GITHUB_TOKEN`.

Fichier exemple fourni : `update_config.sample.json`.

### Limite API GitHub (403 rate limit)

Le check est automatiquement limité (cooldown) entre deux ouvertures d'application pour réduire fortement le risque de rate-limit.
Si nécessaire, ajoutez un token local (non versionné) pour fiabiliser encore plus.

### Gestion d'échec renforcée

- détection d'échec de copie dans le script de remplacement ;
- backup rollback (`.old`) si le remplacement échoue ;
- ouverture optionnelle d'un lien de téléchargement manuel (`manual_url`) en cas d'échec.

### Structure recommandée du code

- `utf8_converter_gui.py` : UI Tkinter et orchestration.
- `text_conversion.py` : logique de conversion/encodage/langue.
- `updater.py` : configuration updater + intégration GitHub Releases.

### Limites connues

- Le remplacement automatique est prévu pour l'application packagée (`.exe`, mode PyInstaller).
- Si l'EXE est installé dans un dossier protégé (ex. Program Files), un mécanisme élévation/UAC dédié pourra être ajouté dans une étape suivante.

---

## 10. Licence

MIT.

---

## 11. Sécurité du token GitHub

Le projet fonctionne sans token GitHub, mais un token local améliore la fiabilité.

Si vous ajoutez un token localement :

1. Ne mettez jamais un vrai token dans un fichier suivi par Git.
2. Le fichier `update_config.json` est local et ignoré par `.gitignore`.
3. Préférez la variable d'environnement `UTF8CONVERTER_GITHUB_TOKEN`.

Vérifications avant push :

```powershell
git status --short
git diff --cached
```

Si `update_config.json` a déjà été ajouté par erreur :

```powershell
git rm --cached update_config.json
```

Puis regenérez un nouveau token si vous pensez qu'il a pu fuiter.

---
