# OGX Branch Protection Governance

## 1) Stratégie de branches par domaine

- **Production**: `main`
- **Intégration**: `develop`
- **Stabilisation**: `release/*`
- **Correctifs urgents**: `hotfix/*`
- **Domaines produit**:
  - `thara/*` (THARA)
  - `ogx-prime/*` (OGX PRIME)
- **Domaines techniques**:
  - `os/*`
  - `minios/*`
  - `cores-os/*`

## 2) Rulesets GitHub (versionnés)

Les règles sont définies dans:
- `.github/rulesets/critical-branches.json` (strict)
- `.github/rulesets/feature-branches.json` (standard)

### Principes clés
- PR obligatoire sur branches critiques
- **2+ approbations** sur branches critiques
- Checks obligatoires: build, tests, qualité, sécurité
- Interdiction force-push/suppression sur critiques
- Commits signés requis sur critiques
- Merge queue requise sur critiques

## 3) Ownership des modules internes

Le fichier `.github/CODEOWNERS` impose des propriétaires pour:
- `/os/`
- `/minios/`
- `/cores-os/`
- `/agents/`

Aucun merge ne doit passer si un owner requis n'a pas validé.

## 4) Séparation des droits par équipe

### Modèle cible
- Squad **THARA**: écriture sur `thara/*`
- Squad **OGX PRIME**: écriture sur `ogx-prime/*`
- Admin plateforme: groupe restreint uniquement

### Contraintes
- Aucune suppression de branche/tag critique sans privilège admin
- Aucun bypass permanent des règles critiques

> Note: Les permissions fines d'équipe se configurent côté GitHub (repo/org settings).

## 5) Break-glass contrôlé

Une exception est autorisée uniquement si:
1. Incident bloquant confirmé
2. Approbation explicite d'un admin plateforme
3. Ticket d'exception créé (cause, périmètre, durée)
4. Expiration automatique de l'exception
5. Revue post-incident obligatoire

## 6) Audit et KPI

Audit mensuel minimum:
- nombre de bypass
- nombre d'échecs checks obligatoires
- temps moyen de review
- taux de PR conformes
- incidents évités / détectés

Les résultats servent à ajuster rulesets et capacité squads.

## 7) Déploiement progressif

- **Phase 1**: `main`, `thara/*`, `ogx-prime/*`
- **Phase 2**: `os/*`, `minios/*`, `cores-os/*`
- **Phase 3**: durcissement final (merge queue stricte, signatures, sécurité renforcée)

## 8) Application des rulesets via GitHub API (optionnel)

Exemple (à exécuter par un admin):

```bash
gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  /repos/DudeStunna1/ogx-systems/rulesets \
  --input .github/rulesets/critical-branches.json

gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  /repos/DudeStunna1/ogx-systems/rulesets \
  --input .github/rulesets/feature-branches.json
```
