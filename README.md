## LÉGENDE
- [W]  = utiliser concepts Wagtail natifs (Page, Snippet, Image, StreamField, RoutablePage, ModelAdmin UI).  
- [W?] = usage partiel Wagtail (exposer via ModelAdmin, stocker assets dans Wagtail Images).  
- [D]  = logique Django classique (UGC, jobs, modération, billing, workers).

---

# 1) APP: core
But : mixins, timestamps, UUIDs, helpers partagés, permission helpers.

ASCII - modèles & éléments
```
[CoreTimestampMixin]  [D]
- created_at (datetime)
- updated_at (datetime)

[UUIDMixin]  [D]
- uuid (uuid4 unique)

[PermissionHelpers] [D]
- helper functions: is_company_admin(user, company), can_view_internal(user, company)
```

Comportements & intégration
- Fournit fields réutilisés par la majorité des modèles (Post, AIJob, etc.).  
- Permet standardiser audit/logging.  
- Aucun usage Wagtail spécifique (mais ModelAdmin et pages peuvent s’appuyer sur les mixins).

---

# 2) APP: accounts
But : custom user model, gestion membres / vérification domaine, invites, rôles.

ASCII - modèles & éléments
```
[User] [D]
- id PK
- email (unique)                 # AUTH_USER_MODEL
- username
- first_name, last_name
- is_active, is_staff, is_superuser
- preferred_pseudo_template      # ex: "L'ombre de la RH #{n}"
- settings JSON
- created_at

[CompanyMember] [D]
- id PK
- user -> User (FK)
- company -> Company (FK)
- role (enum: member, admin, hr, moderator)
- is_verified (bool)             # verified via email @domain
- verified_at
- created_at

[DomainVerificationToken] [D]
- id PK
- company -> Company (FK)
- token (string)
- email (string)
- status (pending/verified/expired)
- created_at
```

Comportements & intégration
- User = custom AUTH_USER_MODEL (D). Wagtail utilise automatiquement le AUTH_USER_MODEL pour son admin.  
- CompanyMember.is_verified est la clef d’accès au mur interne (internal feed).  
- Vérification domaine flow :
  - user signs up with @example.com -> send verification email (background) -> on confirm, set is_verified and link to Company (create Company if domain not exist) -> if domain matches Company, CompanyMember created/updated.
- Exposer User / CompanyMember via Wagtail ModelAdmin pour RH/marketing ([W?]) si on veut gestion non-tech.

Permissions & roles
- CompanyMember.role définit droits (assign internal posts, respond, manage members).
- Use PermissionHelpers in core to centralize checks.

HTMX / UI
- Endpoints HTMX : login, signup, verify-token modal, invite flow.  
- UX : verification modal / toast.

Indexation & recherche
- User searchable in admin only (no full-text public).

---

# 3) APP: companies
But : Company record, CompanyAlias public, alias editable by marketing via Snippets.

ASCII - modèles & éléments
```
[Company] [D]
- id PK
- domain (unique, nullable)          # example.com
- name (official, nullable)
- description (text, internal)
- is_premium (bool)                  # subscription state (derived from billing)
- plan -> Plan (FK, billing)
- created_at, updated_at

[CompanyAlias] [W? -> Snippet recommended]
- id PK
- alias_name (unique)                # "Société #42 — Projet Orion"
- slug (unique)                      # stable slug used in alias landing page
- public_description (text)
- company -> Company (FK nullable)    # null if unclaimed
- public_badge (FK -> Badge snippet?) [W?]
- created_at

[Lead] [D]
- id PK
- company_guess (string)              # guessed name from mention
- source_post -> Post (FK nullable)
- contacted (bool)
- assigned_to -> User (sales)
- created_at
```

Comportements & intégration
- Company = logique métier, crée link avec CompanyAlias when company claims alias (via verification of domain).  
- CompanyAlias should be a Wagtail Snippet so marketing can edit public description/badge/images ([W]). CompanyAlias retains FK to Company so system knows if claimed.  
- When Mention detected and Company.is_premium == False => create Lead (sales pipeline).  
- Company admin exposed via ModelAdmin in Wagtail (W?) to allow non-techs to inspect.

UI / Routage
- AliasLandingPage (RoutablePage in cms app) will map slug -> CompanyAlias snippet to render public feed & marketing content ([W]).

Index & constraints
- Company.domain unique. CompanyAlias.alias_name unique and slug unique. Mention uniqueness to avoid duplicates.

---

# 4) APP: cms / marketing (Wagtail-first)
But : all marketing pages, alias landing pages, newsletter templates, snippets, badges, Wagtail Images.

ASCII - composants (Wagtail)
```
PAGES [W]
- HomePage (Page)              # StreamField layout blocks
- PricingPage (Page)
- AliasLandingPage (RoutablePage)  # route: /alias/<slug>/ => loads CompanyAlias snippet + posts
- NewsletterPage (Page)         # archive / send preview

SNIPPETS [W]
- CompanyAlias Snippet         # alias_name, slug, description, hero_image (wagtailimage), badge
- Badge Snippet                # name, icon (wagtailimage), description
- MarketingTag Snippet         # (option)

IMAGES / DOCUMENTS [W]
- Wagtail Images used to store generated visuals / mèmes / card images
- Use image renditions & CDN features
```

Comportements & intégration
- Marketing editors manage CompanyAlias via Snippets UI; when editing alias, they can update public_description, hero image, badge ([W]).  
- AliasLandingPage (RoutablePage) renders posts that reference CompanyAlias.slug (query posts in Posts app) and uses StreamField to build BLOCKS for marketing content.  
- Newsletters built with NewsletterPage, possibly integrated with marketing app subscriber lists.

Admin exposure & ModelAdmin
- Use ModelAdmin to expose Django models (Company, Post, InternalPost) in the Wagtail admin menu for moderators and RH ([W?]).  
- Wagtail Pages handle SEO/landing pages while Post content remains in Django DB.

HTMX / UI snippets
- Alias page supports AJAX loading (htmx) for feed pagination, filters by tag/tone.  
- Sharing CTA on pages to produce social posts with watermark.

Notes & best-practices
- Do not convert Post into Wagtail Page. Use Posts as Django models but render via Wagtail templates on AliasLandingPage.  
- Store AI-generated images in Wagtail Images so marketing can reuse.  
- Wagtail only for editorial content and public presentation layer.

---

# 5) APP: posts
But : UGC model, tags, mentions, sarcasm score, generated media link.

ASCII - modèles & éléments
```
[Post] [D]
- id PK
- author -> User (FK nullable)        # null if anonymous not logged in
- pseudo (string)                     # auto-generated pseudonym
- text (text)
- tone (enum: ironique, rage, desabusé, etc.)
- tags M2M -> Tag
- is_public (bool)                    # True -> displayed on public feed
- is_internal (bool)                  # True -> indicates company-targeted
- company_alias -> CompanyAlias (FK nullable)
- sarcasm_score (float)               # computed by AI
- generated_title (string)
- generated_image -> wagtailimages.Image (FK nullable) [W?]
- created_at
- updated_at

[Tag] [D or W?]
- id PK
- name (unique)
```

Autres entités reliées
```
[Mention] [D]
- id PK
- post -> Post (FK)
- company -> Company (FK)
- confidence (float)
- created_at
```

Comportements (signals, BG jobs)
- On Post.save:
  - Fire background tasks:
    - AIJob(type=detect_mentions) -> creates Mention(s) if confidence > threshold.
    - AIJob(type=sarcasm_score) -> set sarcasm_score.
    - AIJob(type=generate_title, gen_image) -> generate title + image and save into Wagtail Images (link to generated_image).
    - Moderation check -> if violation -> create ModerationQueue entry.
  - If Mention(s) exist:
    - For each Mention.company:
      - If company.is_premium -> create InternalPost (internal app) and notify CompanyMembers verified.
      - Else -> create Lead (companies app).
- Tagging: tags can be either Django model or Wagtail Snippet editable by marketing (W?) depending on need.

Admin / UI
- Posts exposed via Wagtail ModelAdmin for moderators and RH panel ([W?]). Provide filters: tone, tags, sarcasm_score, company_alias, created_at.
- Public feed served via Django views but can be embedded in Wagtail templates (AliasLandingPage).

HTMX endpoints & interactions
- Post creation via HTMX form:
  - returns snippet of the new post on success (rendered fragment).
  - optimistic UI: show pending state while AI jobs run.
- Filters via hx-get to load filtered posts.

Indexation & search
- Index Post into Meilisearch/Elasticsearch:
  - fields: id, text, pseudo, tags, tone, sarcasm_score, is_public, created_at, company_alias.slug.
- Use tsvector for quick Postgres full-text fallback.

Privacy & Anonymisation
- Scrub PII before saving text (PII filter in moderation pipeline).  
- Pseudo generated algorithmically; ensure uniqueness and rate-limit to avoid being deanonymized.

---

# 6) APP: internal
But : internal feed per company, InternalPost, Response objects, workflow tracking.

ASCII - modèles & éléments
```
[InternalPost] [D]
- id PK
- post -> Post (FK)                    # original user confession
- company -> Company (FK)
- visible_to_company (bool)
- status (enum: new, in_progress, resolved, archived)
- assigned_to -> CompanyMember (FK nullable)
- created_at
- updated_at

[Response] [D]
- id PK
- internal_post -> InternalPost (FK)
- sender_member -> CompanyMember (FK nullable)
- sender_user -> User (FK nullable)
- content (text)
- mediated_content (text)               # AI rephrasing for empathy
- is_anonymous (bool)                   # always true for original employee
- created_at
```

Comportements & intégration
- Creation:
  - When Mention detected and Company.is_premium: create InternalPost and notify company members (via Notification app).
  - InternalPost visible only to verified CompanyMember users (CompanyMember.is_verified).
- Responses:
  - Company admins/RH can craft responses; optionally pass through AIJob(mediate_response) to produce mediated_content.
  - Response posted to internal feed; original poster receives anonymized notification (if opted-in) but cannot see responder identity.
- Timeline:
  - InternalPost includes a timeline (history of assigned_to, status changes, responses) for audit. Timeline stored as events or as part of InternalPost history table.
- Expose InternalPost & Response via ModelAdmin in Wagtail for RH use ([W?]) and via dedicated company dashboard (D).

Permissions & access control
- Access internal feed only to users who are CompanyMember with is_verified True and with appropriate role.  
- Admin UI to manage assignments and status transitions.

HTMX / UI
- Company dashboard uses HTMX to:
  - load lists, filter by status, assign posts, add response (modal).
  - timeline updates in-place.

Exports & integrations
- Dashboard allows CSV/PDF export of InternalPosts and timeline (via background job if large).  
- Integrations app can forward internal events to Slack/Teams/Notion via configured connectors.

---

# 7) APP: ai
But : orchestrer jobs AI (sarcasm scoring, classification, title/image gen, mediation), credit accounting.

ASCII - modèles & éléments
```
[AIJob] [D]
- id PK
- post -> Post (FK nullable)
- internal_post -> InternalPost (FK nullable)
- company -> Company (FK nullable)
- job_type (enum: detect_mentions, sarcasm, gen_title, gen_image, mediate_response, classify_tone)
- status (pending/running/completed/failed)
- result_json (JSONField)
- cost_credits (int)
- created_at
- started_at
- completed_at

[AIJobLog] [D]
- id PK
- aijob -> AIJob (FK)
- message (text)
- created_at
```

Comportements & intégration
- Triggered by signals (Post.save -> create appropriate AIJobs).  
- Worker pool (Celery/RQ) picks up AIJobs and calls provider (OpenAI, internal model).  
- On success:
  - update Post.sarcasm_score, generated_title, link generated_image stored to Wagtail Images, classification label stored in Post or AIJob.result_json.
  - decrement credits in Company Credit usage (billing app).  
- If AI image generated -> call service to create wagtailimages.Image asset and set Post.generated_image FK ([W?]).  
- Moderation usage: AI may flag posts for moderation (enqueue ModerationQueue).

Credit accounting
- Each AIJob consumes credits; credits tracked per company in CreditUsage (billing app).  
- If company over quota -> AIJobs may be restricted or require pre-purchase credits.

Admin & visibility
- AIJobs visible in admin (ModelAdmin) for monitoring ([W?]).  
- Retry & inspect logs in AIJobLog.

Notes
- Keep result_json for transparency and audit.  
- Provision for caching, rate-limits, and provider fallbacks.

---

# 8) APP: moderation
But : queue, rules, human/moderator actions, PII scrubbing.

ASCII - modèles & éléments
```
[ModerationQueue] [D]
- id PK
- post -> Post (FK)
- reason (enum: profanity, personal_data, illegal, harassment, other)
- status (open/closed)
- priority (int)
- created_at

[ModerationAction] [D]
- id PK
- moderation -> ModerationQueue (FK)
- action (enum: delete, hide, warn_user, escalate_to_legal)
- actor -> User (FK)
- note (text)
- created_at
```

Comportements & intégration
- Auto-moderation:
  - On Post.save -> run automated checks (bad-word lists, PII detector, AI flagging). If flagged, create ModerationQueue entry.  
- Human moderation:
  - Moderators access a queue UI (ModelAdmin in Wagtail or a custom moderator app) to review and take actions.  
- Actions:
  - delete: remove post from public feed, keep in archive for audit.
  - hide: mark is_public=False.
  - warn_user: send notification / temp-ban.
  - escalate: notify legal / support.
- Logs:
  - Store actions in ModerationAction for audit.

UI & HTMX
- Moderator UI uses HTMX for quick actions (hide/delete/warn) with modals and batch operations.

Integration points
- On delete/hide -> if post had InternalPost link, optionally notify Company admin (depends on policy).  
- PII scrubbing module sits here or in ai pipeline.

Notes on workflow
- Wagtail Pages workflow NOT recommended for UGC; use custom moderation pipeline (D).

---

# 9) APP: billing
But : plans, subscriptions, invoices, credits IA, badges, whitelist/white-label options.

ASCII - modèles & éléments
```
[Plan] [D]
- id PK
- name (Free, Boss Basic, Boss Pro, Boss Enterprise)
- price_monthly (decimal)
- features JSON
- created_at

[Subscription] [D]
- id PK
- company -> Company (FK)
- plan -> Plan (FK)
- status (active, canceled, past_due)
- started_at
- canceled_at
- stripe_subscription_id (optional)
- created_at

[Invoice] [D]
- id PK
- subscription -> Subscription (FK)
- amount (decimal)
- status
- issued_at

[CreditUsage] [D]
- id PK
- company -> Company (FK)
- month (date)
- credits_used (int)
- created_at

[Badge] [W? / Snippet]
- id PK
- name
- description
- image -> wagtailimages.Image (W)
- public_display (bool)
```

Comportements & intégration
- Subscription activation -> set Company.is_premium True -> enable alias claiming & internal feed.  
- Credits:
  - AIJob completion decrements company credits; if over limit, block some AI features or bill overage.  
- Badge:
  - purchasable "Entreprise à l'écoute" badge displayed on CompanyAlias page if enabled (Snippet or relation) ([W?]).  
- Billing integration with Stripe/Paddle: webhooks to update Subscription & Invoice.  
- Expose Plan & Subscription via Wagtail ModelAdmin ([W?]) for marketing.

Monétisation options encoded
- Monthly plans, credits, badge purchase, integrations paid, white-label offering.

HTMX / UI
- Billing dashboard for company admins (show usage, buy credits, change plan). HTMX interactions for quick upgrade modals.

Notes
- Ensure GDPR compliance for invoice data retention and exports.

---

# 10) APP: integrations
But : connectors Slack/Teams, Webhooks, Notion, API tokens.

ASCII - modèles & éléments
```
[Integration] [D]
- id PK
- company -> Company (FK)
- type (slack, teams, webhook, notion)
- config JSON
- active (bool)
- created_at

[WebhookEventLog] [D]
- id PK
- integration -> Integration (FK)
- payload JSON
- status (sent, failed)
- attempted_at
```

Comportements & intégration
- On InternalPost creation / status change -> if company has Integration.active -> send event to configured connectors (Slack channel, Teams webhook, Notion page).  
- Integrations configurable by company admins in company dashboard (W? via ModelAdmin).  
- Security: generate per-integration tokens; encrypt sensitive config.

UI
- Integration setup wizards in company dashboard (htmx) to authorize Slack, Teams (OAuth flows), or to setup webhooks (URL + secret).

Notes
- Retry logic and logging in WebhookEventLog.  
- Option to map events to Slack messages templates (use Wagtail snippets for templates if desired).

---

# 11) APP: notifications
But : in-app, email queue, opt-ins, newsletter subscriptions.

ASCII - modèles & éléments
```
[Notification] [D]
- id PK
- recipient_user -> User (FK nullable)
- company -> Company (FK nullable)
- type (enum: email, in_app, slack)
- payload JSON
- is_sent (bool)
- send_after (datetime nullable)
- created_at
```

Comportements & intégration
- On InternalPost creation or Response posted -> queue Notification(s) to company admins or to original post author (anonymized).  
- Email sending via provider (SES/Sendgrid) in background.  
- Newsletter subscriptions managed in marketing app & Wagtail (Signup forms integrated with marketing list).

Admin & UI
- Notification logs viewable via ModelAdmin (W?).  
- Settings per user for notification preferences (User.settings JSON).

---

# 12) APP: analytics
But : aggregate stats, alerts, emotional health score.

ASCII - modèles & éléments
```
[AggregateStat] [D]
- id PK
- company -> Company (FK nullable)
- metric_key (string)                  # e.g., meetings_complaint_pct
- value (float)
- period_start (date)
- period_end (date)
- created_at

[Alert] [D]
- id PK
- company -> Company (FK)
- reason (text)
- severity (enum: low, medium, high)
- triggered_by (AIJob/Moderation ref)
- created_at
- resolved_at (nullable)
```

Comportements & intégration
- Periodic background aggregation tasks compute metrics from Posts/InternalPosts (daily/weekly/monthly).  
- AI signals feed alerts (e.g., 5 mentions about IT dept in 7 days -> create Alert).  
- Dashboard displays:
  - Top complaint types, times & peaks, sarcasm index, emotional health score (composite).  
- Export CSV/PDF from dashboard (background job if many rows).

Admin & UI
- Analytics surfaced in Company dashboard (D) and optionally via Wagtail admin for superusers (W?).

---

# 13) APP: search
But : full-text search for Posts (Meilisearch/Elastic). Wagtail search reserved for Pages.

ASCII - composants & index schema
```
Search Index (external) [D]
- Index name: posts
  - id
  - text (full-text)
  - pseudo
  - tags
  - tone
  - sarcasm_score
  - is_public
  - created_at
  - company_alias_slug

- Index company_alias for alias search (optional)
```

Comportements & intégration
- On Post.save -> update search index via background job.  
- Search endpoints:
  - Public search for feed (filters: tone, tag, sarcasm_score range, popularity).  
  - Admin search in Wagtail ModelAdmin for Posts.  
- Use pg_trgm + tsvector fallback if external service down.

---

# 14) APP: marketing
But : newsletter subscriptions, share tracking, watermarks for shared images.

ASCII - modèles & éléments
```
[NewsletterSubscription] [D]
- id PK
- email
- source (alias page, social)
- confirmed (bool)
- created_at

[ShareTracking] [D]
- id PK
- post -> Post (FK)
- platform (string)
- click_count
- first_shared_at
```

Comportements & intégration
- Weekly newsletter generation uses Posts selected by AI (top sarcasm score or editor picks) and NewsletterPage templates in Wagtail ([W]).  
- Social share creates watermark on images (generate via AIJob/gen_image or via on-demand rendering saved to Wagtail Images) ([W?]).  
- Tracking for virality metrics (feeded to analytics).

---

# Cross-app flows résumé (ASCII)
```
[User posts] -> Post saved (posts app)  [D]
   |
   +-> Signal -> enqueue AIJob: detect_mentions, sarcasm_score, gen_title, gen_image  [D -> W? for images]
   |        |
   |        +-> AIJob detects Mention -> create Mention(s) (posts app)  [D]
   |              |
   |              +-> For each Mention.company:
   |                   - If company.is_premium: create InternalPost (internal app) -> notify CompanyMembers (notifications) [D]
   |                   - Else: create Lead (companies app) for sales [D]
   |
   +-> Signal -> moderation checks -> if flagged -> create ModerationQueue (moderation app) [D]
   |
   +-> AIJob gen_image -> save image into Wagtail Images (cms app) -> link Post.generated_image [W?]
   |
   +-> index Post into Search (search app) [D]
```

---

# Admin/UI exposure & Wagtail mapping (ASCII)
```
Wagtail Admin UI [W]
- Pages: HomePage, PricingPage, AliasLandingPage, NewsletterPage
- Snippets: CompanyAlias, Badge, MarketingTag
- Images: Wagtail Images store (generated visuals)

Wagtail ModelAdmin (W?)
- Expose Django models for non-tech users:
  - Post (for moderation)
  - Company (companies app)
  - InternalPost, Response (internal app)
  - Plan, Subscription (billing)
  - ModerationQueue (moderation)
- ModelAdmin gives list_display, filters, search for non-tech editors.

Django Admin (D)
- Developer-facing admin for deep operations, migrations, raw logs.
```

---

# Endpoints / HTMX interactions (résumé ASCII)
```
Frontend (htmx) endpoints examples:
- POST /posts/create/          -> create new Post, return fragment for feed (optimistic)
- GET  /posts/feed/            -> fetch feed page/fragment (filters via query)
- GET  /alias/<slug>/posts/    -> load alias feed fragment (for AliasLandingPage)
- POST /internal/<id>/assign/  -> assign internal post (company admin)
- POST /internal/<id>/respond/ -> submit response (mediated by AI if selected)
- POST /accounts/verify-token/ -> verify company email token
- POST /billing/upgrade/       -> trigger checkout (stripe) modal
- GET  /search/posts/?q=...    -> search posts (filters applied)
```

---

# Indexes, constraints et recommandations techniques (ASCII)
```
Indexes recommandés:
- Post (is_public, created_at)
- Post (company_alias_id, created_at)
- Post (tsvector on text)
- Mention (company_id)
- AIJob (status, created_at)
- AggregateStat (company_id, period_start)

Contraintes & Unique:
- Company.domain unique (if provided)
- CompanyAlias.slug unique
- Post tags -> M2M
- Mention unique(post, company) to avoid duplicates

Tâches background:
- Celery / RQ workers + Redis
- Jobs: AIJob.run, indexer.update_post, moderation.check, export.csv generation, billing webhook handling

Search infra:
- Meilisearch or Elastic for Posts; Wagtail search reserved to Pages.

Images & assets:
- Store AI-generated images as wagtailimages.Image to leverage renditions/CDN
```

---

# Permissions & sécurité (ASCII)
```
- Auth: custom User model (D); Wagtail uses AUTH_USER_MODEL
- CompanyMember.is_verified required for internal access
- CompanyMember.role controls assign/respond/manage
- Wagtail groups/permissions configured for pages/snippets
- Django permissions used for models (view/add/change/delete)
- Rate-limiting posts per IP / per account to avoid abuse
- PII scrubbing in moderation pipeline; retain audit logs for legal
- Encrypt integration credentials; secure webhooks
```

---

# Checklist d’implémentation / priorités (ASCII)
```
Sprint 1 (MVP content & infra)
- Setup Django + Wagtail minimal site
- Implement User (custom), Company, CompanyMember, Post models
- Implement CompanyAlias as Wagtail Snippet
- Implement AliasLandingPage (RoutablePage) to render alias feed
- Implement Post creation via HTMX
- Wire Wagtail ModelAdmin to expose Post, CompanyAlias

Sprint 2 (AI & Moderation)
- Add AIJob model + worker infra
- Implement sarcasm scoring & mention detection AIJobs
- Implement ModerationQueue & auto-moderation rules
- Save generated images to Wagtail Images

Sprint 3 (Premium & Internal)
- Implement Billing Plan & Subscription models + Stripe integration
- Implement InternalPost & Response flows
- Implement CompanyMember verification flow (email domain)
- Expose Internal dashboard (ModelAdmin + company-facing UI)

Sprint 4 (Scale & Analytics)
- Implement search indexing (Meili/Elastic)
- Implement analytics aggregates & alerts (AI)
- Implement exports & integrations (Slack/Teams)
- Implement credits & overage billing logic
```

