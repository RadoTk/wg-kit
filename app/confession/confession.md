# Posts Application - Documentation

## Overview

The Posts application manages user-generated content (UGC) for the "Dear Boss" platform. It handles employee posts, complaints, feedback, and other anonymous content. The application implements sophisticated content analysis, tagging, mention detection, and AI-driven processing for sarcasm scoring, title generation, and image creation. This is a Django-focused application with partial Wagtail integration for generated media assets.

**Classification**: [D] - Django-focused logic with partial Wagtail integration [W?]

## Purpose

The Posts application enables:

- Anonymous employee content submission
- Advanced content analysis (sarcasm, tone, sentiment)
- Automated mention detection for companies
- Content tagging and categorization
- AI-driven content enhancement (titles, images)
- Integration with internal company feeds
- Sales lead generation for non-premium companies

## Models

### Post

**Classification**: [D] - Django Model

The core user-generated content model:

- `id` - Primary key
- `author` - Nullable ForeignKey to User (null for anonymous posts)
- `pseudo` - Auto-generated pseudonym for anonymous content
- `text` - Main text content of the post
- `tone` - Enum field (ironique, rage, desabusé, etc.) for content classification
- `tags` - Many-to-many relationship to Tag model
- `is_public` - Boolean indicating if displayed on public feed
- `is_internal` - Boolean indicating company-targeted content
- `company_alias` - Nullable ForeignKey to CompanyAlias for company association
- `sarcasm_score` - Float computed by AI
- `generated_title` - AI-generated title string
- `generated_image` - Nullable ForeignKey to Wagtail Image [W?] for AI-generated images
- `created_at`, `updated_at` - Timestamp fields

- Anonymous posting with generated pseudonyms
- Tone classification and sarcasm scoring
- Company mention and targeting
- Content filtering (public/internal)
- AI-generated enhancements

### Tag

**Classification**: [D] or [W?] - Django Model or Wagtail Snippet

Content categorization system:

- `id` - Primary key
- `name` - Unique tag name
- Can be implemented as Django model or Wagtail Snippet for marketing management

### Mention

**Classification**: [D] - Django Model

Company mention detection from posts:

- `id` - Primary key
- `post` - ForeignKey to Post model
- `company` - ForeignKey to Company model
- `confidence` - Float representing detection confidence
- `created_at` - Timestamp for mention detection

**Features**:
- Automated company mention detection
- Confidence scoring for accuracy
- Link between posts and companies
- Trigger for internal feed and lead generation

## Automated Processing

### Signal-Based Workflows

When a Post is saved, the system automatically:

1. **Enqueues AI Jobs** for:
   - Mention detection (AIJob with type=detect_mentions)
   - Sarcasm scoring (AIJob with type=sarcasm_score)
   - Title generation (AIJob with type=generate_title)
   - Image generation (AIJob with type=gen_image)
   - Moderation checks (creates ModerationQueue entry if violations detected)

2. **Processes Mentions**: For each detected mention:
   - If company.is_premium: Creates InternalPost and notifies verified CompanyMembers
   - If not premium: Creates Lead in sales pipeline (companies app)

## Content Management

### Tagging System

- Flexible tagging implementation (Django model or Wagtail Snippet)
- Marketing editable if implemented as snippet
- Content categorization for filtering and discovery
- Support for multiple tags per post

### Moderation Integration

- Automatic moderation checks on post creation
- Integration with moderation application queue
- Content filtering and approval workflows
- Violation detection and handling

## Admin Interface

### ModelAdmin Exposure [W?]

Posts exposed via Wagtail ModelAdmin for:

- Moderator and HR panel access
- Filtering options: tone, tags, sarcasm_score
- Company_alias, date filtering
- Content moderation workflows
- Batch operations and analysis

### Public Feed Integration

- Served via Django views
- Embeddable in Wagtail templates (AliasLandingPage)
- Filtering and pagination capabilities
- Real-time content display

## HTMX Integration

### Frontend Endpoints

- **Post Creation**: HTMX form returning rendered post snippets
- **Optimistic UI**: Shows pending state during AI processing
- **Filters**: hx-get for filtered post loading
- **Pagination**: Dynamic content loading

### Interactive Features

- Real-time content updates
- Dynamic filtering by tone, tags, sarcasm
- Responsive post interactions
- Content refresh during AI processing

## Search and Indexation

### External Search Integration

Primary search index (Meilisearch/Elasticsearch) with fields:
- id, text, pseudo, tags, tone, sarcasm_score
- is_public, created_at, company_alias.slug
- Full-text search capabilities
- Advanced filtering options

### Fallback Search

- PostgreSQL full-text search using tsvector
- Database-based search if external service unavailable
- Basic search functionality assurance

## Privacy and Anonymisation

### PII Protection

- PII scrubbing in moderation pipeline
- Anonymous pseudonym generation algorithm
- Unique pseudonym validation and rate limiting
- Privacy-focused content handling

### Anonymization

- Content anonymization for internal feeds
- Pseudonym uniqueness enforcement
- Deanonymization prevention measures
- Privacy compliance measures

## AI Integration [W?]

### Generated Assets

- AI-generated titles and content
- AI-generated images stored in Wagtail Images
- Link between Post and generated Wagtail Images
- Media asset optimization and renditions

## Extensibility

### Adding New Features

The posts system can be extended by:

- Adding new tone classifications
- Implementing additional AI processing tasks
- Creating new content analysis features
- Adding custom filtering and sorting options
- Extending the tagging system
- Adding content interaction features

## Security Considerations

- Content validation and sanitization
- Pseudonym system security
- AI processing security during generation
- Content moderation and approval flows
- User privacy and anonymity protection
- Rate limiting for post submissions
- PII data protection and scrubbing

## Dependencies

- Django's model and admin systems
- Core application for mixins (if used)
- Accounts application for user relationships
- Companies application for mentions
- AI application for processing
- Moderation application for content review
- Internal application for internal posts
- Wagtail Images for generated content [W?]
- Search infrastructure for indexing