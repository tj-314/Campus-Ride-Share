# Campus Ride Share - recreated starter

This is a newly regenerated classroom prototype, not the instructor's Jest examples, not a finished system, and not an implementation of the Request Seat booking diagram. It follows the posting-focused SRS. Resolve the design mismatch with your instructor before claiming these modules are the design-milestone classes.

## Windows setup

Clone or download this repository and open the folder containing app.py.
Open PowerShell in that folder. Run commands one at a time; stop on errors.

```powershell
py -m venv .venv
.\\\\.venv\\\\Scripts\\\\python.exe -m pip install -r requirements.txt
.\\\\.venv\\\\Scripts\\\\python.exe app.py
```

Open http://127.0.0.1:5000 in your browser. Choose an active demo identity. Use fictional contact data. Use a future date to make a post appear in Browse. My Posts shows owned past posts too. Data persists in rides.db. Stop server with Ctrl+C.

## Tests (another terminal in the same folder)

```powershell
.\\\\.venv\\\\Scripts\\\\python.exe -m pytest -v
.\\\\.venv\\\\Scripts\\\\python.exe -m pytest --cov=models --cov=service --cov-branch --cov-report=term-missing
```

Save your actual output for the worksheet. Named TC IDs are proposed mappings, not completed worksheet rows. Tests use temporary databases. PostService tests include database integration; do not call all of them isolated unit tests.

## Components/data

* models.py: RidePost.validate and ValidationError.
* service.py: PostService SQLite CRUD, filters, owner authorization.
* app.py and templates/: Flask browser interface, server-side demo identity allow-list, signed sessions, CSRF checks.
* posts table: id, owner (demo identity), post\_type, destination, travel\_date (YYYY-MM-DD), departure\_time (HH:MM), contact (free text), seats (integer or null).
* authorize\_owner in service.py labels three outcomes for white-box planning. Coverage includes untested paths; no coverage percentage is promised.

## Scope and limitations

Authentication is a DEMONSTRATION, not real SEMO verification or instructor approval. HTTP localhost does NOT meet NFR-04 HTTPS. Do not expose the app publicly. Do not enter real personal data. Official identity integration, deployment security, browser testing, performance, load and usability measurements remain unverified.

Implemented starter workflows: offer/request creation, required fields, owner storage, confirmation, type labels, browse, combined destination/date filters, protected details/contact, My Posts, owner edit and confirmed deletion. Do not claim all SRS requirements are verified.

Assumptions requiring review: seats integer >=1 without maximum; destination case-insensitive substring matching; date and destination combined using AND; old posts hidden from Browse (SRS expiry policy TBD); free-text contact format (TBD); fixed post type during edit. Valid past dates can be created. No seat reservations, payments, GPS, chat or automated matching.

Local session key changes at restart unless SECRET\_KEY is set. Current local cookie settings are not deployment hardening. SQLite is a local persistent database. This application is for learning/testing only.

## Disclosure

Perplexity generated this starter and tests. Tag X until independently reviewed; use A only after review and execution consistent with worksheet instructions. Do not backdate implementation or call it earlier team work.

