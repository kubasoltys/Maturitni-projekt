# Před použitím

## Spoustění aplikace

- **první spuštění** : `docker-compose up --build`
- **následující spuštění** : `docker-compose up`

- Aplikace bude dostupná na adrese: `http://localhost:8000`

- **Důležitá poznámka** : Aplikace běží na Dockeru, tudíž je potřeba mít nainstalovaný docker. Databáze je připojená k projektu ale pouze na mém stroji, tudíž se data musí stáhnout ze souboru v projektu.
- Takže další krok, vytvoření tabulek : `docker compose exec web python manage.py migrate`
- Stažení dat ze souboru : `docker compose exec web python manage.py loaddata fixtures/dumpdata.json`

## Při změně v databázi

- Aby se změny v databázi uložily do souboru dumpdata.json, je potřeba spustit příkaz : `docker compose exec web python dump.py`