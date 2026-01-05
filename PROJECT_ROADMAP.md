# Reading List Project Roadmap

Your personal action plan for building a multi-user AI Reading List platform.

---

## Phase 1: Complete Email Forwarding Setup (Now)
**Goal**: Get email forwarding working so you can forward newsletters and articles

### ✅ Code Status
All code is implemented and ready! Just need to configure the external service.

### 🎯 Action Steps

1. **Install ngrok** (for local testing)
   - Download from https://ngrok.com/download
   - Move to `/usr/local/bin/`
   - Verify with `ngrok version`

2. **Start ngrok tunnel**
   - Open new terminal tab
   - Run: `ngrok http 5001`
   - Copy the `https://` URL (e.g., `https://abc123.ngrok-free.app`)

3. **Create SendGrid account** (Free tier: 100 emails/day)
   - Go to https://sendgrid.com
   - Sign up with your email
   - Verify your email address

4. **Configure SendGrid Inbound Parse**
   - Settings → Inbound Parse → Add Host & URL
   - URL: `https://YOUR-NGROK-URL.ngrok-free.app/api/ingest`
   - Save and get your forwarding email address

5. **Test it!**
   - Forward a Stratechery email to the SendGrid address
   - Or send an email with article URLs
   - Check your Reading List app - articles should appear!

**Estimated Time**: 30 minutes

---

## Phase 2: Chrome Extension for Easy Capture
**Goal**: Save articles from any webpage with one click

### What You'll Build
- Chrome extension with a simple "Save to Reading List" button
- Appears in toolbar and on right-click menu
- Automatically extracts article title, URL, and content
- Sends to your Reading List API

### Action Steps

1. **Create extension structure**
   - `manifest.json` - Extension configuration
   - `background.js` - Handles button clicks
   - `content.js` - Extracts article content from page
   - `popup.html` - Optional popup UI

2. **Implement content extraction**
   - Use Mozilla's Readability.js or similar
   - Extract title, author, main content
   - Send to `/api/articles` endpoint

3. **Test locally**
   - Load unpacked extension in Chrome
   - Test on various news sites

4. **Package for Chrome Web Store** (optional)
   - Create developer account ($5 one-time fee)
   - Publish extension

**Estimated Time**: 2-4 hours

**Resources**:
- Chrome Extension docs: https://developer.chrome.com/docs/extensions/
- Readability.js: https://github.com/mozilla/readability

---

## Phase 3: Deploy to Vercel (Production)
**Goal**: Host app in the cloud so it runs 24/7

### Why Vercel?
- Free tier with plenty of resources
- Easy Python/Flask deployment
- Custom domains
- Auto-scaling

### Action Steps

1. **Upgrade database from SQLite to PostgreSQL**
   - SQLite doesn't work well on serverless platforms
   - Use Vercel Postgres (free tier available)
   - Or use Neon, Supabase, or Railway for database

2. **Add `vercel.json` configuration**
   ```json
   {
     "builds": [{ "src": "app.py", "use": "@vercel/python" }],
     "routes": [{ "src": "/(.*)", "dest": "app.py" }]
   }
   ```

3. **Add `requirements.txt` updates for production**
   - Add `psycopg2-binary` for PostgreSQL
   - Add `gunicorn` for production server

4. **Create Vercel account**
   - Go to https://vercel.com
   - Sign up with GitHub

5. **Connect GitHub repo to Vercel**
   - Import your `testing` repo
   - Configure environment variables (.env values)
   - Deploy!

6. **Update SendGrid webhook**
   - Change from ngrok URL to permanent Vercel URL
   - E.g., `https://your-app.vercel.app/api/ingest`

7. **Test everything**
   - Web interface
   - Email forwarding
   - Daily digest automation
   - Chrome extension (update API URL)

**Estimated Time**: 3-5 hours

**Note**: Daily digest will now run automatically in the cloud at 8 AM every day!

---

## Phase 4: Landing Page + User Sign Up
**Goal**: Professional landing page that explains the product and allows sign ups

### What You'll Build
- Clean, modern landing page
- Sign up form (just email to start)
- Product description and features
- How it works section
- Call-to-action buttons

### Action Steps

1. **Design landing page**
   - Hero section with value proposition
   - Features list (AI summaries, email digests, etc.)
   - How it works (3 simple steps)
   - Sign up form
   - Optional: Testimonials, screenshots

2. **Create new route** `/landing` or make it the home page
   - Move current app to `/app` or `/dashboard`
   - Landing page at `/`

3. **Build sign up form**
   - Email input
   - Optional: Name, preferences
   - Stores in new `users` table

4. **Add email confirmation**
   - Send welcome email via SendGrid
   - Include instructions for forwarding emails
   - Include their unique forwarding address

**Estimated Time**: 4-6 hours

**Design Inspiration**:
- Instapaper, Pocket, Matter (reading apps)
- Simple, clean, focused on value proposition

---

## Phase 5: Multi-User Authentication
**Goal**: Each user has their own account, articles, and feed

### What You'll Build
- User registration and login system
- Session management
- Password hashing
- Each user's articles isolated from others

### Action Steps

1. **Add authentication library**
   - Flask-Login for session management
   - Werkzeug for password hashing
   - Or use Auth0/Clerk for easier setup

2. **Create user tables**
   ```sql
   users: id, email, password_hash, name, created_at
   user_articles: links articles to users
   user_preferences: digest time, forwarding email, etc.
   ```

3. **Update all endpoints to be user-scoped**
   - `/api/articles` - only show logged-in user's articles
   - `/api/digest/send` - only send user's articles
   - Etc.

4. **Build login/register pages**
   - Registration form
   - Login form
   - Password reset flow
   - Protected routes (require login)

5. **Update email webhook**
   - Parse "To:" address to determine which user
   - Each user gets unique forwarding address
   - E.g., `user123@reading.yourdomain.com`

**Estimated Time**: 6-10 hours

---

## Phase 6: Admin Dashboard
**Goal**: You can see all users, their activity, and usage stats

### What You'll Build
- Admin-only dashboard
- User list with stats
- Activity feed (recent articles added, digests sent)
- Usage metrics (articles per user, etc.)
- Ability to view any user's feed

### Action Steps

1. **Create admin role**
   - Add `is_admin` field to users table
   - Set your account as admin

2. **Build admin dashboard** (`/admin`)
   - Protected route (admin only)
   - User list with search/filter
   - Stats: total users, articles, digests sent

3. **User detail pages** (`/admin/users/:id`)
   - View user's articles
   - View their activity
   - Send test digest
   - Manage their account

4. **Analytics dashboard**
   - Charts: Users over time, articles added per day
   - Popular sources
   - Engagement metrics

**Estimated Time**: 6-8 hours

---

## Phase 7: Polish & Launch
**Goal**: Make it production-ready and invite first users

### Final Touches

1. **Custom domain** (optional)
   - Buy domain (e.g., readinglist.ai)
   - Configure with Vercel
   - Update SendGrid for email forwarding

2. **Email improvements**
   - Better email templates
   - Unsubscribe link
   - Email preferences page

3. **Error handling**
   - Better error messages
   - Failed article notifications
   - Retry logic for email delivery

4. **Onboarding flow**
   - Welcome email with setup instructions
   - Tutorial on first login
   - Sample articles to demo features

5. **Invite friends!**
   - Share landing page
   - Get feedback
   - Iterate based on usage

**Estimated Time**: 4-8 hours

---

## Total Timeline Estimate

- **Phase 1** (Email setup): 30 min
- **Phase 2** (Chrome extension): 2-4 hours
- **Phase 3** (Vercel deployment): 3-5 hours
- **Phase 4** (Landing page): 4-6 hours
- **Phase 5** (Multi-user auth): 6-10 hours
- **Phase 6** (Admin dashboard): 6-8 hours
- **Phase 7** (Polish): 4-8 hours

**Total**: ~26-42 hours of development

**Suggested Approach**:
- Phase 1: Do today (30 min)
- Phases 2-3: This week (1-2 days)
- Phases 4-5: Next week (2-3 days)
- Phases 6-7: Following week (2-3 days)

---

## Next Immediate Steps

### Right Now (30 minutes):
1. Download and install ngrok
2. Create SendGrid account
3. Configure email forwarding webhook
4. Test by forwarding a newsletter

### This Week:
1. Build Chrome extension
2. Deploy to Vercel
3. Update all URLs to production

### Next Week:
1. Build landing page
2. Add user authentication
3. Invite first beta users

---

## Questions to Consider

Before building multi-user:
- **Pricing**: Free to start? Premium features later?
- **Limits**: Max articles per user? Max emails per day?
- **Privacy**: Can users make their reading lists public/shareable?
- **Social**: Ability to follow other users' reading lists?
- **Export**: Let users export their data?

You can decide these as you build!

---

## Tech Stack Summary

**Current (Single User)**:
- Python/Flask
- SQLite
- Anthropic Claude API
- SendGrid (email)
- Vanilla JS frontend

**Future (Multi-User)**:
- Same stack, plus:
- PostgreSQL (scalable database)
- Flask-Login (authentication)
- Vercel (hosting)
- Custom domain
- Chrome Extension

---

Ready to get started with Phase 1? Let me know when you have ngrok installed and we'll set up SendGrid together!
