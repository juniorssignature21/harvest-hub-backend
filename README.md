# Abiagrow.connect — Back-End (Django)

This README summarizes the recent work done in this repository and explains how to run and test the project locally.

## Project summary

Abiagrow.connect is a Django-based backend for a marketplace connecting farmers and merchants. Recent changes implemented in this branch focus on:

- Email verification flow for new users (token generation, verification view, resend flow).
- Fixes to user registration and authentication (password handling and login correctness).
- Restrictions so only email-verified users can access protected areas.
- Product/image upload improvements allowing multiple images per product.
- Tailwind CSS integration (Django-tailwind-compatible config + CDN/no-npm option and templates).
- Several new templates and a base layout using Tailwind utilities.
- A management command to reset unusable passwords created earlier during testing.


## What was changed / added

- `userauths/`
  - `models.py`: Added `token_created_at` to `CustomUser` to track verification token creation time.
  - `views.py`: Reworked registration (ensures password hashed), added email verification view, resend view, login checks that prevent unverified users from logging in, and logout view. Applied a decorator to require email verification for some views.
  - `forms.py`: Registration now uses Django's `UserCreationForm` (password1/password2 flow).
  - `utils.py`: Sends verification and welcome emails and uses namespaced reverse for verification links.
  - `decorators.py`: New `email_verification_required` decorator to protect views.
  - `management/commands/reset_unusable_passwords.py`: Management command to reset passwords for users with unusable passwords (those whose password field begins with `!`).
  - Templates: `templates/userauths/login.html`, `register.html`, `home.html` (improved UI), and registration templates `signup_success.html` and `resend_verification.html`.

- `store/`
  - `models.py`: `ProductImage` model exists for multiple images per product.
  - `forms.py`: `AddProductForm` updated to exclude the single `image` field so the view can accept multiple files. (File input handled in template and view.)
  - `views.py`: `add_product` and `edit_product` save the product first, then create `ProductImage` instances from `request.FILES.getlist('image')`.
  - Templates: `templates/farmers/addproduct.html` updated to include `enctype="multipart/form-data"` and an `<input name="image" multiple>` field.

- Tailwind / assets
  - `tailwind.config.js`: Tailwind configuration was added with project content paths and theme colors.
  - `package.json`: Scripts for building/watching Tailwind (optional - npm workflow).
  - `theme/static_src/src/styles.css` and `theme/static/css/style.css` placeholders exist.
  - `TAILWIND_SETUP.md`: Documentation for setting up Tailwind (both npm and no-npm CDN options).
  - `templates/base.html`: Base template referencing compiled CSS under static files (the project also supports a CDN/no-npm option during development if desired).

- Misc
  - Added `templates/store/dashboard.html` and other UI templates.


## Important notes / caveats

- Migrations: After adding `token_created_at` to `CustomUser`, you must run migrations. When attempting to run `makemigrations` earlier, Django failed to start in this environment due to a missing optional admin package (`jazzmin`). Install the project dependencies and run migrations locally:

```bash
pip install -r requirements.txt   # if you have one
# or at least
pip install jazzmin

python3 manage.py makemigrations
python3 manage.py migrate
```

- Email: Configure email settings in `Agrosite/settings.py` (SMTP or console backend). In development you can use the console backend to see email bodies in the terminal:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

- Tailwind: There are two supported workflows:
  - npm (recommended for production): run `npm install` then `npm run tailwind:watch` (dev) or `npm run tailwind:build` (production). This generates `theme/static/css/style.css` which is referenced by `base.html`.
  - no-npm (quick dev): Use Tailwind CDN by enabling the CDN variant of the base template (this project includes a documented CDN option in `TAILWIND_SETUP.md`). Note: CDN includes the full Tailwind runtime, not tree-shaken, so it's not optimal for production.

- Multiple images handling: The UI now submits multiple files under the `image` field name (input uses `multiple`). The `AddProductForm` excludes the `image` model field; the `add_product`/`edit_product` views iterate `request.FILES.getlist('image')` and create `ProductImage` records. Ensure `MEDIA_ROOT`/`MEDIA_URL` are configured and writable.

- Authentication: Login was changed to authenticate by `username`. If you prefer login-by-email, implement a custom authentication backend.


## How to run locally (recommended flow)

1. Create and activate a virtualenv, install Python deps:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt   # or install packages manually
```

2. Install node (optional, for Tailwind npm workflow) and run:

```bash
npm install
npm run tailwind:watch
```

3. Run migrations and start Django:

```bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
```

4. Register a user at `/userauths/register/` and check the console/email for the verification link. Use the resend page at `/userauths/resend-verification/` if needed.


## Quick troubleshooting

- "No file was submitted" or "FileInput doesn't support uploading multiple files": ensure your form has `enctype="multipart/form-data"` and the template uses an `<input name="image" multiple>`; views use `request.FILES.getlist('image')`.

- Login failing with valid credentials: ensure the username/password are correct and the account email is verified (the login view prevents unverified accounts from logging in). If a user's password field starts with `!` the password is unusable; run the provided management command to reset usable passwords:

```bash
python3 manage.py reset_unusable_passwords --password NewPass123!
```


## Next steps / recommendations

- Add unit tests for registration, email verification and product image uploading.
- Add server-side validation for image count, file size, and file type in `add_product`.
- Implement an email verification token cleanup or reuse policy (short-lived tokens).
- Consider allowing login by email via a custom authentication backend.
- Replace CDN Tailwind usage with a production npm build and `collectstatic` for deployment.


## Contact / Ownership

Repository owner: Agroplug-com
Project lead / commit contact: the current workspace owner


---

If you'd like, I can now:
- Add server-side image validation and limits to the `add_product` view,
- Create unit tests for the verification flow,
- Or produce a small script to bulk-fix passwords for specific users.

Tell me which you'd like next and I'll proceed.