# JZ MCU — Notifications YouTube vers Discord

Ce petit bot vérifie régulièrement les chaînes YouTube de tes créateurs et poste automatiquement un message dans ton salon Discord dès qu'une nouvelle vidéo sort. Il tourne gratuitement dans le cloud via GitHub Actions — pas besoin de laisser un PC allumé.

Créateurs suivis actuellement :
- **Iro Sef**
- **Kevin Bukkart**

Pour en ajouter ou en retirer, modifie le dictionnaire `CREATORS` en haut du fichier `jzmcu_bot.py`.

## Mise en ligne (une seule fois, ~5 minutes)

### 1. Créer le dépôt GitHub

1. Va sur [github.com](https://github.com) et connecte-toi (ou crée un compte gratuit).
2. Clique sur **New repository** (bouton vert en haut à droite).
3. Donne-lui un nom, par exemple `jz-mcu-bot`.
4. Laisse-le en **Private** si tu préfères (fonctionne pareil).
5. Clique sur **Create repository**.

### 2. Envoyer les fichiers de ce dossier dans le dépôt

Le plus simple sans ligne de commande :
1. Sur la page de ton nouveau dépôt, clique sur **uploading an existing file** (ou **Add file → Upload files**).
2. Glisse-dépose **tous les fichiers et dossiers** de ce dossier `jz-mcu-bot` (y compris le dossier `.github` avec le fichier workflow à l'intérieur — vérifie qu'il est bien inclus, GitHub l'affiche parfois discrètement).
3. Clique sur **Commit changes**.

### 3. Ajouter ton webhook Discord comme secret (important, ne jamais le mettre en clair dans le code)

1. Dans ton dépôt GitHub, va dans **Settings** (onglet en haut).
2. Dans le menu de gauche : **Secrets and variables → Actions**.
3. Clique sur **New repository secret**.
4. Nom : `DISCORD_WEBHOOK_URL`
5. Valeur : colle l'URL de ton webhook Discord (celle que tu as créée dans Salon → Modifier le salon → Intégrations → Webhooks).
6. Clique sur **Add secret**.

### 4. Activer et tester le bot

1. Va dans l'onglet **Actions** de ton dépôt.
2. Si GitHub demande de confirmer l'activation des workflows, clique sur **I understand my workflows, go ahead and enable them**.
3. Clique sur le workflow **JZ MCU - Vérification des vidéos** dans la liste à gauche.
4. Clique sur **Run workflow** (bouton à droite) pour le lancer manuellement une première fois.
5. Attends ~30 secondes puis rafraîchis — tu dois voir une coche verte ✅.

**Important pour la toute première exécution :** le bot ne poste RIEN au premier lancement, il se contente de mémoriser la dernière vidéo déjà en ligne de chaque créateur (pour ne pas spammer d'anciennes vidéos). À partir de la 2e exécution, toute nouvelle vidéo sera bien annoncée dans Discord.

Ensuite, il tourne tout seul toutes les 15 minutes, pour toujours. Tu n'as plus rien à faire.

## Vérifier que ça fonctionne

- Onglet **Actions** de ton dépôt : chaque exécution apparaît dans la liste avec une coche verte (succès) ou une croix rouge (erreur). Clique dessus pour voir le détail des logs si besoin.
- Le fichier `state.json` du dépôt se met à jour automatiquement à chaque nouvelle vidéo détectée — tu peux l'ouvrir pour voir les derniers IDs de vidéos mémorisés.

## Modifier la fréquence de vérification

Dans `.github/workflows/jzmcu.yml`, la ligne `cron: "*/15 * * * *"` veut dire "toutes les 15 minutes". Tu peux la changer, par exemple :
- `*/5 * * * *` → toutes les 5 minutes
- `*/30 * * * *` → toutes les 30 minutes
- `0 * * * *` → une fois par heure

Évite de descendre sous 5 minutes : GitHub Actions est gratuit mais limite le nombre d'exécutions par mois sur les comptes gratuits (2000 minutes/mois), et une vérification toutes les 15 min consomme très peu (largement dans la limite gratuite).

## Sécurité

Ne partage jamais l'URL de ton webhook Discord publiquement (capture d'écran, message public, dépôt GitHub non protégé par secret...). N'importe qui la possédant peut poster des messages dans ton salon. Si elle a fuité, supprime le webhook dans Discord (Salon → Intégrations → Webhooks) et recrée-en un nouveau, puis mets à jour le secret `DISCORD_WEBHOOK_URL` sur GitHub.
