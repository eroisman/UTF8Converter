# UTF-8 Text Converter

Convertisseur graphique pour textes et sous-titres qui :
- détecte l’encodage, convertit en UTF-8 et corrige éventuellement le texte (mojibake) ;
- détecte automatiquement la langue et ajoute un suffixe (`-heb`, `-eng`, etc.) aux fichiers convertis ;
- gère le drag & drop des fichiers dans l’interface ;
- permet de forcer l’encodage d’entrée, de choisir un dossier de sortie, de créer des sauvegardes `.bak` et de suivre la progression via une barre et un journal.

---

## 1. Fonctionnalités principales

- **Supports** : `.txt`, `.srt`, `.ass`, `.vtt`, `.md`, `.csv`, etc.
- **Interface Windows** (Tkinter + ttk) avec icône personnalisable.
- **Auto-détection** de l’encodage (via `chardet`) et conversion en UTF-8.
- **Corrections automatiques** (optionnelles) avec `ftfy`.
- **Langue** détectée via `langdetect` avec renommage automatique (`nom-heb.srt`, `nom-eng.txt`, …).
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

- **Ajoutez/éditez** les suffixes de langue dans le dictionnaire `LANG_SUFFIXES`.
- Adaptez la liste des encodages proposés (`ENCODINGS`).
- Modifiez les extensions prises en charge (`SUPPORTED_EXTENSIONS`).
- Ajoutez d’autres fonctionnalités (ex. mémorisation des réglages, previews, etc.).

---

## 9. Licence

MIT.

---
