# Deploying to Vercel

This guide walks you through deploying your Reading List app to Vercel for production use.

## Why Vercel?

- **Free tier** with generous limits
- **Serverless** - always running, no server management
- **Auto-scaling** - handles traffic spikes automatically
- **Custom domains** - free SSL certificates
- **Permanent URL** - perfect for SendGrid webhook
- **Cron jobs** - automated daily digests

---

## Step 1: Set Up PostgreSQL Database

Vercel's serverless environment doesn't support SQLite, so you need a PostgreSQL database. **Neon** has the best free tier:

### Create Neon Database (Recommended - Free)

1. Go to https://neon.tech
2. Sign up with GitHub
3. Click **"Create a project"**
4. Choose:
   - **Project name**: `reading-list`
   - **Region**: Choose closest to you
   - **PostgreSQL version**: Latest (16)
5. Click **"Create project"**
6. Copy the **connection string** - it looks like:
   ```
   postgresql://username:password@ep-xxx.us-east-2.aws.neon.tech/neondb
   ```
7. Save this - you'll need it for Vercel!

**Alternative**: Vercel Postgres, Supabase, or Railway also work great

---

## Step 2: Deploy to Vercel

### A. Sign Up for Vercel

1. Go to https://vercel.com/signup
2. Click **"Continue with GitHub"**
3. Authorize Vercel to access your GitHub account

### B. Import Your Project

1. From Vercel dashboard, click **"Add New..."** → **"Project"**
2. Find your `testing` repository
3. Click **"Import"**

### C. Configure Build Settings

Vercel should auto-detect Flask. If not, set:
- **Framework Preset**: Other
- **Build Command**: (leave empty)
- **Output Directory**: (leave empty)
- **Install Command**: `pip install -r requirements.txt`

### D. Add Environment Variables

Click **"Environment Variables"** and add these:

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DATABASE_URL=your_neon_connection_string_here
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_gmail_address
SMTP_PASSWORD=your_gmail_app_password
DIGEST_RECIPIENT=your_email_address
DIGEST_TIME=08:00
```

**Important**: Use the exact same values from your local `.env` file!

### E. Deploy!

1. Click **"Deploy"**
2. Wait 1-2 minutes for the build to complete
3. You'll get a URL like: `https://testing-abc123.vercel.app`

**Your app is now live!** 🎉

---

## Step 3: Test Your Deployment

1. Visit your Vercel URL: `https://your-app.vercel.app`
2. Try adding an article
3. Check that it appears in the interface
4. Test the "Send Digest" button

---

## Step 4: Configure SendGrid Webhook

Now that you have a permanent URL, set up email forwarding:

1. Go to SendGrid dashboard: https://app.sendgrid.com
2. Navigate to **Settings** → **Inbound Parse**
3. Click **"Add Host & URL"**
4. Enter your Vercel URL:
   ```
   https://your-app.vercel.app/api/ingest
   ```
5. Click **"Add"**
6. SendGrid will give you an email address like:
   ```
   parse@inbound.sendgrid.net
   ```

### Test Email Forwarding

1. Forward a newsletter to the SendGrid address
2. Wait 10-15 seconds
3. Refresh your Reading List app
4. The article should appear!

---

## Step 5: Automated Daily Digest

Your app is configured to send digests at 8:00 AM daily via Vercel Cron Jobs.

### How It Works

The `vercel.json` file includes:
```json
"crons": [
  {
    "path": "/api/digest/send",
    "schedule": "0 8 * * *"
  }
]
```

This automatically hits your `/api/digest/send` endpoint every day at 8 AM.

### Change Digest Time

1. Update `vercel.json` to change the schedule:
   - `0 8 * * *` = 8:00 AM daily
   - `0 20 * * *` = 8:00 PM daily
   - `0 12 * * 1` = Noon on Mondays
2. Commit and push changes - Vercel auto-deploys!

---

## Step 6: Custom Domain (Optional)

Want a custom domain like `reading.yourdomain.com`?

1. Buy a domain (Namecheap, Google Domains, etc.)
2. In Vercel dashboard:
   - Go to your project
   - Click **"Settings"** → **"Domains"**
   - Add your domain
   - Follow DNS instructions
3. Update SendGrid webhook to use your custom domain

---

## Troubleshooting

### Build Fails

**Error**: `Module not found: psycopg2`
- **Fix**: Make sure `psycopg2-binary==2.9.9` is in `requirements.txt`

**Error**: `No module named 'anthropic'`
- **Fix**: Verify `requirements.txt` has `anthropic>=0.40.0`

### Database Connection Fails

**Error**: `could not connect to server`
- **Fix**: Double-check the `DATABASE_URL` environment variable in Vercel
- Make sure you copied the full connection string from Neon

### Email Digest Not Sending

**Error**: Digest doesn't arrive at 8 AM
- **Fix**: Check Vercel logs for errors (Functions → your-app → Logs)
- Verify `SMTP_PASSWORD` has no spaces
- Test manually by visiting `https://your-app.vercel.app/api/digest/send`

### SendGrid Webhook Not Working

**Error**: Forwarded emails don't appear in app
- **Fix**: Check Vercel Function logs for incoming requests
- Verify the webhook URL in SendGrid matches your Vercel URL exactly
- Try sending a test email and check SendGrid's Activity Feed

---

## Viewing Logs

To debug issues:

1. Go to Vercel dashboard
2. Click on your project
3. Go to **"Deployments"**
4. Click on the latest deployment
5. Click **"Functions"** to see logs

---

## Updating Your App

Vercel automatically deploys when you push to GitHub:

1. Make changes locally
2. Commit: `git add . && git commit -m "your message"`
3. Push: `git push`
4. Vercel auto-deploys in ~1 minute!

---

## Free Tier Limits

**Vercel Free Tier**:
- 100 GB bandwidth/month
- 100 hours of serverless function execution/month
- Unlimited deployments

**Neon Free Tier**:
- 0.5 GB storage
- 1 project
- Always-on database

**SendGrid Free Tier**:
- 100 emails/day
- Inbound Parse included

**These limits are more than enough for personal use!**

---

## Next Steps

Once deployed:
1. ✅ Share the Vercel URL with friends to beta test
2. ✅ Build the Chrome extension (point it to Vercel URL)
3. ✅ Add user authentication for multi-user support
4. ✅ Create a landing page

---

## Support

- **Vercel Docs**: https://vercel.com/docs
- **Neon Docs**: https://neon.tech/docs
- **SendGrid Docs**: https://docs.sendgrid.com

Your app is now production-ready! 🚀
