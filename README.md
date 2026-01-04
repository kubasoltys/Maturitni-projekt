# Squadra – Webová aplikace pro správu fotbalového týmu

## 📌 Cíl projektu

Cílem projektu **Squadra** je vytvořit moderní, přehlednou a responzivní webovou aplikaci, která umožní fotbalovým týmům efektivně spravovat své hráče, plánovat zápasy a tréninky, sledovat docházku a uchovávat základní statistiky.

---

## 🛠️ Použité technologie

Projekt bude využívat:

- **Frontend:**
  - `HTML` – Struktura webových stránek
  - `Tailwind CSS` – Moderní utility-first framework pro stylování
  - `Chart.js` – Grafy pro vizualizaci statistik
  - `Font Awesome` – Ikony pro lepší vizuální přehlednost
  - `JavaScript` – Interaktivita a dynamické prvky na stránce

- **Backend:**
  - `Python` – Jako hlavní programovací jazyk
  - `Django` – Webový framework pro správu databáze, uživatelských účtů a logiky aplikace
  - `Docker` – Kontejnerizace aplikace pro zajištění stejného vývojového prostředí a snadnou správu závislostí.'

- **Databáze:**
  - `SQLite` – (Zkušební) Ukládání dat o hráčích, zápasech, statistikách a uživatelích
  - `PostgreSQL` – Pouze cíl, hlavní databáze projektu

---

## ✅ Obsah aplikace v bodech

Chtěl bych, aby aplikace obsahovala:

- **Uživatelský systém**
  - Registrace a přihlášení uživatelů
  - Role: trenér, admin a hráč
  - Základní správa profilu (heslo, kontaktní údaje, profilová fotka)

- **Správa hráčů**
  - Přidávání, editace a mazání hráčů
  - Evidování základních údajů (jméno, číslo dresu, pozice, věk, kontakt)
  - Seznam hráčů s vyhledáváním a filtrováním

- **Zápasy a tréninky**
  - Vytváření událostí (datum, čas, soupeř, místo)
  - Přehledný seznam všech akcí
  - Detail zápasu s výsledkem a klíčovými statistikami

- **Docházka**
  - Možnost potvrdit účast hráče na zápasu/tréninku
  - Přehled docházky pro trenéra

- **Dashboard**
  - Zobrazení nadcházejících zápasů a tréninků
  - Souhrn základních statistik (počet hráčů, odehraných zápasů, výhry/prohry)

---

## 🗓️ Časový harmonogram

| Období        | Cíl                                                                 |
|---------------|---------------------------------------------------------------------|
| **Září**      | Návrh struktury aplikace, tvorba základního UI, napojení na databázi |
| **Podzim**    | Vylepšování vzhledu stránky (Tailwind), doplňování funkcí, testování a ladění |
| **Konec roku**| Práce na volitelných funkcích, responzivita, nové nápady, příprava prezentace |

---

## 📚 Zdroje

* [PostgreSQL Tutorial](https://www.postgresql.org/docs/current/tutorial.html)
* [Tailwind CSS](https://tailwindcss.com/)
* [Django Authentication - Topics](https://docs.djangoproject.com/en/5.2/topics/auth/)
* [Django Authentication - Groups](https://docs.djangoproject.com/en/5.2/topics/auth/default/#groups)
* [Chart.js - Getting Started](https://www.chartjs.org/docs/latest/getting-started/)
* [Chart.js - Samples](https://www.chartjs.org/docs/latest/samples/)
* [Font Awesome Docs](https://fontawesome.com/docs)
* [Mermaid.js](https://mermaid.js.org/)
* [Django Custom User Model (TestDriven.io)](https://testdriven.io/blog/django-custom-user-model/)
* [W3Schools Online Web Tutorials](https://www.w3schools.com/)
* [W3Schools - CSS Modals](https://www.w3schools.com/howto/howto_css_modals.asp)
* [How to Dockerize a Django App (Docker Blog)](https://www.docker.com/blog/how-to-dockerize-django-app/)
* [Django PostgreSQL Migration from SQLite](https://www.youtube.com/watch?v=ZgRkGfoy2nE&t=589s)
* [Docker With Django Tutorial | How To Dockerize A Django Application](https://www.youtube.com/watch?v=BoM-7VMdo7s)